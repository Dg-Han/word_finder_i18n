import re
import json

from tkinter import *
from tkinter import ttk

dict_path = "test.json"
#dict_path = "zh_hans_characters.json"
with open(dict_path, "r", encoding="utf-8") as f:
    raw_str = f.read()

zh_hans_dict:dict = json.loads(raw_str)
"""
zh_hans_dict内容:
- key: 汉字(utf-8)
- values:
    - index: 通用规范汉字表编号
    - full: 全拼list
    - ic: 声母list
    - vowel: 韵母list
    - tone: 声调
    - strokes: 笔画数
    - cc: 汉字电码(待补充)
    - fc: 四角号码(待补充)
"""

word_dict_path = "zh_hans_words.txt"
with open(word_dict_path, "r", encoding="utf-8") as f:
    raw_str = f.read()
word_dict = raw_str.split("\n")
    
class UI(Frame):
    def __init__(self, master = None, *args, **kwargs) -> None:
        super().__init__(master)
        for key in kwargs:
            setattr(self, key, kwargs[key])

        self.master.title("Word Finder")
        self.master.geometry("1600x900")

        self.lb1 = Label(self.master, text="请选择汉字个数")
        self.cmb1 = ttk.Combobox(self.master, values= ["1", "2", "3", "4"])
        self.cmb1.bind("<<ComboboxSelected>>", self.update_finder)
        self.lb1.place(relx=0.4, rely=0.1, width=100, height=25)
        self.cmb1.place(relx=0.5, rely=0.1, width=100, height=25)
    
    def update_finder(self, event):
        for widget in self.master.winfo_children():
            #print(widget.winfo_name())
            if widget.winfo_name() not in ["!label", "!combobox", "!ui"]:
                widget.destroy()

        n = int(self.cmb1.get())
        self.subwidgets = {"n_chars":n, "ic":[], "vowel":[], "tone":[], "strokes":[]} # type: dict[str, list[ttk.Combobox] | int]
        for _ in range(n):
            lb1 = Label(self.master, text="声母")
            cmb1 = ttk.Combobox(self.master, values=["", "b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"])
            lb2 = Label(self.master, text="韵母")
            cmb2 = ttk.Combobox(self.master, values=["", "a", "o", "e", "i", "u", "v", "ai", "ei", "ui", "ao", "ou", "iu", "ie", "ve", "er", "an", "en", "in", "un", "vn", "ang", "eng", "ing", "ong"])
            lb3 = Label(self.master, text="音调")
            cmb3 = ttk.Combobox(self.master, values=[""] + [str(_) for _ in range(1,5)])
            lb4 = Label(self.master, text="笔画数")
            cmb4 = ttk.Combobox(self.master, values=[""] + [str(_) for _ in range(1,30)])
            lb5 = Label(self.master, text="四角号码")
            lb6 = Label(self.master, text="中文电码")
            cmb1.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            cmb2.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            cmb3.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            cmb4.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            lb1.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.3, relwidth=0.05, relheight=0.025)
            cmb1.place(relx=(2*_+1)/(2*n), rely=0.3, relwidth=0.1, relheight=0.025)
            lb2.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.4, relwidth=0.05, relheight=0.025)
            cmb2.place(relx=(2*_+1)/(2*n), rely=0.4, relwidth=0.1, relheight=0.025)
            lb3.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.5, relwidth=0.05, relheight=0.025)
            cmb3.place(relx=(2*_+1)/(2*n), rely=0.5, relwidth=0.1, relheight=0.025)
            lb4.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.6, relwidth=0.05, relheight=0.025)
            cmb4.place(relx=(2*_+1)/(2*n), rely=0.6, relwidth=0.1, relheight=0.025)
            self.subwidgets["ic"].append(cmb1)
            self.subwidgets["vowel"].append(cmb2)
            self.subwidgets["tone"].append(cmb3)
            self.subwidgets["strokes"].append(cmb4)

    def _get_stricts(self, index:int) -> dict:
        """
        返回第(index+1)组控件的所有非空值
        """
        res = {}
        ic = self.subwidgets["ic"][index].get()
        if ic:
            res["ic"] = ic
        vowel = self.subwidgets["vowel"][index].get()
        if vowel:
            res["vowel"] = vowel
        tone = self.subwidgets["tone"][index].get()
        if tone:
            res["tone"] = tone
        strokes = self.subwidgets["strokes"][index].get()
        if strokes:
            res["strokes"] = strokes
        fc = NotImplemented
        cc = NotImplemented

        return res
    
    def _toplevel_display(self, event, res:str) -> None:
        """
        新建 `tkinter.Toplevel` 窗体显示res内容
        """
        detail = Toplevel(self)
        detail.title("Result")
        detail.geometry("480x360")
        text = Text(detail, width=460, height=360, font=("宋体", 24))
        text.insert(1.0, res)
        sb=Scrollbar(detail)
        sb.pack(side="right", fill="y")
        text.pack(side="left")
        sb.config(command=text.yview)
        text.config(yscrollcommand=sb.set, state="disabled")

        detail.mainloop()

    def update_searcher(self, event, index) -> None:
        """
        点击控件后更新搜索结果及UI
        """
        for widget in self.winfo_children():
            if widget.winfo_class() == "Button":
                widget.destroy()
        stricts = self._get_stricts(index)

        res = []
        for ch in zh_hans_dict:
            b = True
            for con in stricts.keys():
                if con in ["strokes"]:
                    if zh_hans_dict[ch][con] != stricts[con]:
                        b = False
                        break
                elif con in ["ic", "vowel", "tone"]:
                    if stricts[con] not in zh_hans_dict[ch][con]:
                        b = False
                        break
            if b:
                res.append(ch)
        if len(res) <= 10:
            self.lbans = Label(self.master, text=",".join(res), font=("宋体", 12))
            self.lbans.place(relx=(2*index+1)/(2*self.subwidgets["n_chars"]) - 0.075, rely=0.75, relwidth=0.2, relheight=0.05)
        else:
            self.btans = Button(self.master, text=f"共有{len(res)}个结果")
            self.btans.bind("<Button-1>", lambda e: self._toplevel_display(e, res))
            self.btans.place(relx=(2*index+1)/(2*self.subwidgets["n_chars"]) - 0.075, rely=0.75, relwidth=0.2, relheight=0.05)
        if self.subwidgets["n_chars"] > 1:
            self._update_word_searcher()

    def _update_word_searcher(self) -> None:
        stricts_list = []
        for index in range(self.subwidgets["n_chars"]):
            stricts = self._get_stricts(index)
            stricts_list.append(stricts)

        res = []
        for word in word_dict:
            if len(word) != len(stricts_list):
                continue
            for _ in range(len(word)):
                b = True
                for con in stricts_list[_].keys():
                    if con in ["strokes"]:
                        if zh_hans_dict.get(word[_],{"strokes":""})[con] != stricts_list[_][con]:
                            b = False
                            break
                    elif con in ["ic", "vowel", "tone"]:
                        if stricts_list[_][con] not in zh_hans_dict.get(word[_],{"ic":"","vowel":"","tone":""})[con]:
                            b = False
                            break
                if not b:
                    break
            if b:
                res.append(word)
        
        if len(res) <= 10:
            self.lbans = Label(self.master, text=",".join(res), font=("宋体", 12))
            self.lbans.place(relx=0.1, rely=0.85, relwidth=0.8, relheight=0.05)
        else:
            self.btans = Button(self.master, text=f"共有{len(res)}个结果")
            self.btans.bind("<Button-1>", lambda e: self._toplevel_display(e, res))
            self.btans.place(relx=0.4, rely=0.85, relwidth=0.2, relheight=0.05)

if __name__ == "__main__":
    UI().mainloop()