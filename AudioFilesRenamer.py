"""
音频文件批量重命名工具
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import mutagen
class AudioFilesRenamer:
    def __init__(self, length: int, height: int)-> None:
        '''
        初始化图形界面的布局和按钮。
        将背景划分为三部分：顶部按钮区，左边源文件，右边预览区。
        :param length: 窗口长度
        :param height: 窗口高度
        '''
        self.length = length
        self.height = height
        self.root = tk.Tk()
        self.root.title('音频文件批量重命名工具')
        self.root.geometry(f'{self.length}x{self.height}')
        self.source_files = []  # 源文件列表
        self.preview_files = []  # 预览文件列表

        # 添加自定义重命名存储字典
        self.custom_renames = {}

        # 初始化顶部按钮区
        self.init_buttons()

        # 创建主内容区域框架
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 初始化左侧源文件列表
        self.init_source_list() 
        
        # 竖直分割线
        self.separator = tk.Frame(self.content_frame, width=2, bg="#cccccc")
        self.separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # 初始化右侧预览文件列表
        self.init_preview_list()

        # 进入主循环
        self.root.mainloop()



    def init_buttons(self)-> None:
        '''
        初始化顶部按钮区，将按钮放到一行中,居中对齐,按钮之间留有空隙：选择文件夹、创建命名规则、文件名预览、重命名、退出
        '''
        # 创建顶部按钮框架
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, pady=10)

        # 创建按钮并添加到框架
        buttons = [
            ('选择文件夹', self.choose_dir),
            ('创建命名规则', self.create_rename_rule),
            ('文件名预览', self.preview_rename),
            ('重命名', self.rename_files),
            ('退出', self.root.quit)
        ]

        # 遍历创建按钮并设置布局
        for text, command in buttons:
            btn = tk.Button(
                self.button_frame, 
                text=text, 
                width=15, 
                height=2, 
                command=command
            )
            btn.pack(side=tk.LEFT, padx=5)

        # 设置框架居中
        self.button_frame.pack_configure(anchor=tk.CENTER)
        # 在按钮下方画一条水平分割线
        self.separator = tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, padx=5, pady=5)
    


    def init_source_list(self)-> None:
        '''
        初始化左侧源文件列表,框架顶部显示文件名、编号、各种元数据, 底部显示文件数量
        '''
        # 左侧源文件区域的框架
        self.source_frame = tk.Frame(self.content_frame)
        self.source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 顶部标签
        self.source_label = tk.Label(self.source_frame, text=f"源文件列表    文件数量: {len(self.source_files)}")
        self.source_label.pack(pady=5)
        # 文件列表区域
        self.source_listbox = tk.Listbox(self.source_frame)
        self.source_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)



    def init_preview_list(self)-> None:
        '''
        初始化右侧预览文件列表
        '''
        # 右侧预览区域
        self.preview_frame = tk.Frame(self.content_frame)
        self.preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 顶部标签
        self.preview_label = tk.Label(self.preview_frame, text=f"预览文件名列表    文件数量: {len(self.preview_files)}")
        self.preview_label.pack(pady=5)
        # 文件列表区域
        self.preview_listbox = tk.Listbox(self.preview_frame)
        self.preview_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

       


    def choose_dir(self)-> None:
        '''
        选择文件夹，弹出文件夹选择框，选好后在左侧源文件列表中显示文件信息，更新文件数量
        '''
        # 弹出文件夹选择框
        self.dir_path = filedialog.askdirectory(title="选择音频文件夹", initialdir=os.getcwd())
        if self.dir_path:
            # 清空列表
            self.source_listbox.delete(0, tk.END)
            
            # 定义支持的音频文件扩展名
            audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma', '.aac')
            
            # 扫描文件夹并筛选音频文件
            for filename in os.listdir(self.dir_path):
                if filename.lower().endswith(audio_extensions):
                    # 添加到源文件列表
                    self.source_listbox.insert(tk.END, filename)
                    self.source_files.append(filename)
            
            # 更新文件数量显示
            self.source_label.config(text=f"源文件列表    文件数量: {len(self.source_files)}")
        
    

    def create_rename_rule(self)-> None:
        '''
        创建命名规则，弹出窗口让用户选择文件名要出现的元数据类型或加载保存的规则，并保存配置字典文件
        '''
        self.rule_window = tk.Toplevel(self.root)
        self.rule_window.title("创建命名规则")
        self.rule_window.geometry("400x400")
        # 规则选项
        self.rule_options = {
            '原文件名': tk.BooleanVar(value=True),
            '编号': tk.BooleanVar(value=False),
            '艺术家': tk.BooleanVar(value=False),
            '专辑': tk.BooleanVar(value=False),
            '标题': tk.BooleanVar(value=False),
            '年份': tk.BooleanVar(value=False),
            '曲目号': tk.BooleanVar(value=False),
            #'自定义文本': tk.StringVar(value="")
        }
        # 创建复选框
        row = 0
        for key, var in self.rule_options.items():
            # if key == '自定义文本':
            #     tk.Label(self.rule_window, text="自定义文本:").grid(row=row, column=0, padx=5, pady=5)
            #     tk.Entry(self.rule_window, textvariable=var).grid(row=row, column=1, padx=5, pady=5)
            # else:
            #     tk.Checkbutton(self.rule_window, text=key, variable=var).grid(row=row, column=0, padx=5, pady=5)
            # row += 1
            tk.Checkbutton(self.rule_window, text=key, variable=var).grid(row=row, column=0, padx=5, pady=5)
            row += 1
        # 保存按钮
        save_btn = tk.Button(self.rule_window, text="保存规则", command=self.save_rename_rule)
        save_btn.grid(row=row, column=0, padx=5, pady=20)

    def save_rename_rule(self)-> None:
        '''
        保存重命名规则
        '''
        self.rename_rule = {key: var.get() for key, var in self.rule_options.items()}
        print("保存的重命名规则:", self.rename_rule)
        messagebox.showinfo("规则保存", "重命名规则已保存！")
        self.rule_window.destroy()
    
    def preview_rename(self)-> None:
        '''
        预览重命名效果,在预览区中预览每个文件的文件名，返回新文件名列表
        '''
        # 清空预览列表
        self.preview_listbox.delete(0, tk.END)
        self.preview_files = []
        # 预览每个文件的新文件名
        for file in self.source_files:
            filePath = os.path.join(self.dir_path, file)
            new_name = self.generate_new_filename(filePath)
            if new_name:
                self.preview_files.append(new_name)
                self.preview_listbox.insert(tk.END, new_name)
        # 更新预览文件数量显示
        self.preview_label.config(text=f"预览文件名列表    文件数量: {len(self.preview_files)}")
        print("预览的重命名文件列表:", self.preview_files)



    def generate_new_filename(self, filePath: str) -> str:
        '''
        根据规则生成新文件名
        '''
        # 获取文件元数据
        metadata = self.get_metadata(filePath)
        print("文件元数据:", metadata)
        # 处理缺失元数据
        if not metadata:
            metadata = self.handle_missing_metadata(filePath)
        # 根据规则生成新文件名
        newName = ''
        if self.rename_rule.get('原文件名'):
            newName += os.path.splitext(os.path.basename(filePath))[0]
        if self.rename_rule.get('编号'):
            newName += f"_{self.source_files.index(os.path.basename(filePath))+1:02d}"
        if self.rename_rule.get('艺术家'):
            newName += f"_{metadata.get('artist')}"
        if self.rename_rule.get('专辑'):
            newName += f"_{metadata.get('album')}"
        if self.rename_rule.get('标题'):
            newName += f"_{metadata.get('title')}"
        if self.rename_rule.get('年份'):
            newName += f"_{metadata.get('year')}"
        if self.rename_rule.get('曲目号'):
            newName += f"_{metadata.get('track')}"
        # 添加文件扩展名
        newName += os.path.splitext(os.path.basename(filePath))[1]
        return newName
        

    def get_metadata(self, filePath: str)-> dict:
        '''
        获取音频文件的元数据, 返回包含元数据的字典
        '''
        try:
            audio = mutagen.File(filePath)
            metadata = {}
            if not audio:
                return {'artist': '未知艺术家', 'title': '未知标题', 'album': '未知专辑', 'year': '未知年份', 'track': '0'}

            # 提取艺术家信息 (支持ID3和Vorbis格式)
            artist = audio.get('artist') or audio.get('TPE1')
            metadata['artist'] = self._get_first_value(artist) or '未知艺术家'

            # 提取标题信息
            title = audio.get('title') or audio.get('TIT2')
            metadata['title'] = self._get_first_value(title) or '未知标题'

            # 提取专辑信息
            album = audio.get('album') or audio.get('TALB')
            metadata['album'] = self._get_first_value(album) or '未知专辑'

            # 提取年份信息 (从日期中提取年份)
            date = audio.get('date') or audio.get('TDRC') or audio.get('TYER')
            metadata['year'] = self._extract_year(self._get_first_value(date)) or '未知年份'

            # 提取曲目号 (处理如'1/10'格式)
            track = audio.get('tracknumber') or audio.get('TRCK')
            metadata['track'] = self._extract_track(self._get_first_value(track)) or '0'

            return metadata
        except Exception as e:
            print(f"获取元数据失败: {str(e)}")
            return {'artist': '未知艺术家', 'title': '未知标题', 'album': '未知专辑', 'year': '未知年份', 'track': '0'}

    def _get_first_value(self, value):
        '''辅助方法：获取元数据值并处理编码转换'''
        if not value:
            return None
        # 处理 mutagen 的 TextFrame 类型
        if hasattr(value, 'text'):
            value = value.text
        # 处理列表类型值
        if isinstance(value, list):
            value = value[0] if value else None
        # 处理字节类型值的编码转换
        if isinstance(value, bytes):
            # 尝试常见编码解码，解决中文乱码
            for encoding in ['utf-8', 'gbk', 'latin-1']:
                try:
                    return value.decode(encoding)
                except UnicodeDecodeError:
                    continue
            # 所有编码尝试失败时返回原始字节的字符串表示
            return str(value)
        return str(value)
    

    def _extract_year(self, date_str):
        '''辅助方法：从日期字符串中提取年份'''
        if not date_str:
            return None
        # 匹配4位数字年份 (支持YYYY、YYYY-MM-DD等格式)
        import re
        match = re.search(r'\b\d{4}\b', date_str)
        return match.group() if match else None

    def _extract_track(self, track_str):
        '''辅助方法：从曲目号字符串中提取数字'''
        if not track_str:
            return None
        # 匹配数字部分 (支持'1', '1/10', '01'等格式)
        import re
        match = re.search(r'\d+', track_str)
        return match.group().zfill(2) if match else None


    def handle_missing_metadata(self, filePath: str)-> dict:
        '''
        处理元数据缺失情况,弹窗让用户选择输入缺失元数据还是跳过
        '''
        pass

    def rename_files(self)-> None:
        '''
        重命名文件
        '''
        if not self.preview_files or len(self.preview_files) != len(self.source_files):
            messagebox.showwarning("预览文件名错误", "请先生成预览文件名，且预览文件数量应与源文件数量一致！")
            return
        # 执行重命名操作
        for old_name, new_name in zip(self.source_files, self.preview_files):
            old_path = os.path.join(self.dir_path, old_name)
            new_path = os.path.join(self.dir_path, new_name)
            try:
                os.rename(old_path, new_path)
                print(f"重命名: {old_name} -> {new_name}")
            except Exception as e:
                print(f"重命名失败: {old_name} -> {new_name}, 错误: {str(e)}")
        messagebox.showinfo("重命名完成", "所有文件已重命名完成！")
        





if __name__ == '__main__':
    app = AudioFilesRenamer(1500, 800)