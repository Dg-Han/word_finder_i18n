import re
import json

from tkinter import *
from tkinter import ttk

dict_path = "test1.json"
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
        self.subwidgets = {"n_chars":n, "ic":[], "vowel":[], "tone":[], "strokes":[], "cc":[], "fc":[]} # type: dict[str, list[ttk.Combobox] | int]
        for _ in range(n):
            lb1 = Label(self.master, text="声母")
            cmb1 = ttk.Combobox(self.master, values=["", "b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"])
            lb2 = Label(self.master, text="韵母")
            cmb2 = ttk.Combobox(self.master, values=["", "a", "o", "e", "i", "u", "v", "ai", "ei", "ui", "ao", "ou", "iu", "ie", "ve", "er", "an", "en", "in", "un", "vn", "ang", "eng", "ing", "ong"])
            lb3 = Label(self.master, text="音调")
            cmb3 = ttk.Combobox(self.master, values=[""] + [str(_) for _ in range(1,5)])
            lb4 = Label(self.master, text="笔画数")
            cmb4 = ttk.Combobox(self.master, values=[""] + [str(_) for _ in range(1,30)])
            lb5 = Label(self.master, text="中文电码")
            ety1 = Entry(self.master)
            lb6 = Label(self.master, text="四角号码")
            ety2 = Entry(self.master)
            cmb1.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            cmb2.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            cmb3.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            cmb4.bind("<<ComboboxSelected>>", lambda event, index=_: self.update_searcher(event, index))
            ety1.bind("<Return>", lambda event, index=_: self.update_searcher(event, index))
            ety2.bind("<Return>", lambda event, index=_: self.update_searcher(event, index))
            lb1.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.2, relwidth=0.05, relheight=0.025)
            cmb1.place(relx=(2*_+1)/(2*n), rely=0.2, relwidth=0.1, relheight=0.025)
            lb2.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.3, relwidth=0.05, relheight=0.025)
            cmb2.place(relx=(2*_+1)/(2*n), rely=0.3, relwidth=0.1, relheight=0.025)
            lb3.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.4, relwidth=0.05, relheight=0.025)
            cmb3.place(relx=(2*_+1)/(2*n), rely=0.4, relwidth=0.1, relheight=0.025)
            lb4.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.5, relwidth=0.05, relheight=0.025)
            cmb4.place(relx=(2*_+1)/(2*n), rely=0.5, relwidth=0.1, relheight=0.025)
            lb5.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.6, relwidth=0.05, relheight=0.025)
            ety1.place(relx=(2*_+1)/(2*n), rely=0.6, relwidth=0.1, relheight=0.02)
            lb6.place(relx=(2*_+1)/(2*n) - 0.075, rely=0.7, relwidth=0.05, relheight=0.025)
            ety2.place(relx=(2*_+1)/(2*n), rely=0.7, relwidth=0.1, relheight=0.02)
            self.subwidgets["ic"].append(cmb1)
            self.subwidgets["vowel"].append(cmb2)
            self.subwidgets["tone"].append(cmb3)
            self.subwidgets["strokes"].append(cmb4)
            self.subwidgets["cc"].append(ety1)
            self.subwidgets["fc"].append(ety2)

    def _get_stricts(self, index:int) -> dict:
        """
        返回第(index+1)组控件的所有非空值
        """
        res = {}

        def _get_subwidget_val(strict_name, index):
            val = self.subwidgets[strict_name][index].get()
            if val:
                res[strict_name] = val
        
        _get_subwidget_val("ic", index)
        _get_subwidget_val("vowel", index)
        _get_subwidget_val("tone", index)
        _get_subwidget_val("strokes", index)
        _get_subwidget_val("cc", index)
        _get_subwidget_val("fc", index)

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
            b = judge_char_with_stricts(ch, stricts)
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
                b = judge_char_with_stricts(word[_], stricts_list[_])

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

def judge_char_with_stricts(ch:str, stricts:dict) -> bool:
    """
    判断汉字是否符合限制

    Parameters
    ---
    - ch: 中文单字
    - stricts: 限制条件字典，键值白名单，目前可接受键值包括:
        - ic: 声母
        - vowel: 韵母
        - tone: 声调
        - strokes: 笔画数
        - cc: 中文电码, 如输入不为4位则视为无限制
        - fc: 四角号码, 如输入不为4/5位则视为无限制 (长度为4位自动在末尾补通配符)

    Returns
    ---
    - 单字是否符合限制条件的bool值
    """
    res = True
    if zh_hans_dict.get(ch, "") == "":
        return False
    
    for con in stricts.keys():
        if con in ["strokes"]:
            if zh_hans_dict[ch][con] != stricts[con]:
                res = False
                break
        elif con in ["ic", "vowel", "tone"]:
            if stricts[con] not in zh_hans_dict[ch][con]:
                res = False
                break
        elif con in ["fc", "cc"]:
            if con == "fc":
                if len(stricts["fc"]) not in [4,5]:
                    continue

                stricts["fc"] = stricts["fc"] if len(stricts["fc"]) == 5 else stricts["fc"]+"."
                fc_pattern = ""
                for _ in stricts["fc"]:
                    fc_pattern += _ if re.match(r"\d", _) else "."
                if not re.match(fc_pattern, zh_hans_dict[ch].get(con, "")):
                    res = False
                    break
            if con == "cc":
                if len(stricts["cc"]) != 4:
                    continue

                cc_pattern = ""
                for _ in stricts["cc"]:
                    cc_pattern += _ if re.match(r"\d", _) else "."
                if not re.match(cc_pattern, zh_hans_dict[ch].get(con, "")):
                    res = False
                    break
    
    return res

if __name__ == "__main__":
    UI().mainloop()