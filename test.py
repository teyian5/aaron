import pandas as pd
import os
import re

# 定义CSV文件路径
csv_file_path = 'Teyian_p.csv'  # 替换为你的CSV文件路径
output_folder = 'md_file'  # 定义输出文件夹名称
attachments_folder = 'Teyian_p_附件/附件'  # 定义附件文件夹路径

# 检查文件是否存在
if not os.path.exists(csv_file_path):
    print(f"文件 {csv_file_path} 不存在！")
else:
    # 如果输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 使用pandas读取CSV文件
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # 遍历DataFrame的每一行
    for index, row in df.iterrows():
        title = row['title']  # 获取标题
        markdown_content = row['markdown']  # 获取Markdown内容
        
        # 清理文件名中的非法字符
        valid_title = ''.join([c for c in title if c.isalnum() or c in (' ', '_')]).rstrip()
        
        # 定义附件文件夹路径
        attachment_path = os.path.join(attachments_folder, valid_title)
        
        # 检查附件文件夹是否存在
        if os.path.exists(attachment_path):
            # 获取附件文件夹中的所有图片路径
            image_files = [os.path.join(attachment_path, f) for f in os.listdir(attachment_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            
            # 打印调试信息
            print(f"附件路径: {attachment_path}")
            print(f"找到的图片文件: {image_files}")
            
            # 自然排序：提取文件名中的数字部分并按数字排序
            image_files.sort(key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', os.path.basename(x))])
        else:
            print(f"附件文件夹 {attachment_path} 不存在！")
            image_files = []
        
        # 创建以标题命名的.md文件，文件保存在指定文件夹中
        md_file_name = os.path.join(output_folder, f"{valid_title}.md")
        with open(md_file_name, mode='w', encoding='utf-8') as md_file:
            # 将Markdown内容按行分割
            lines = markdown_content.split('\n')
            new_lines = []
            inserted_images = set()  # 用于记录已插入的图片，避免重复插入
            question_number = None  # 初始化 question_number
            image_count = {}  # 用于记录每道题的图片计数

            # 遍历Markdown内容的每一行，找到插入点
            for line in lines:
                # 删除小标题开头的 `-`
                if line.strip().startswith('- '):
                    line = line.lstrip('- ').strip()  # 去掉开头的 `-` 和多余的空格

                # 检查是否是题号的插入点
                match = re.match(r'^(\d+)\.', line.strip())
                if match:
                    question_number = match.group(1)  # 提取题号
                    image_count[question_number] = 0  # 初始化该题的图片计数
                    new_lines.append(line)  # 先将题干行加入新内容
                    
                    # 检查是否存在题干图片
                    img_path = next((f for f in image_files if re.match(rf"img_{question_number}_\d+_\d+\.png", os.path.basename(f))), None)
                    if img_path and img_path not in inserted_images:
                        print(f"插入题干图片: {img_path}")
                        relative_path = os.path.relpath(img_path, start=os.path.dirname(md_file_name))  # 修改为相对于.md文件的路径
                        # 在题干和选项之间插入图片
                        new_lines.append(f"![图片]({relative_path}){{height=\"100px\"}}")
                        inserted_images.add(img_path)
                    else:
                        print(f"未找到匹配的题干图片: img_{question_number}_*")
                    continue  # 跳过后续逻辑，直接处理下一行

                # 检查是否是选项的插入点
                if question_number:  # 确保 question_number 已定义
                    for option in ['A', 'B', 'C', 'D']:
                        if re.match(rf'- {option}\.', line.strip()):  # 匹配选项格式
                            # 去掉选项前的 `-`
                            line = line.replace(f'- {option}.', f'{option}.', 1)
                            
                            # 匹配选项图片
                            img_path = next((f for f in image_files if re.match(rf"img_{question_number}_{option}_\d+\.png", os.path.basename(f))), None)
                            if img_path and img_path not in inserted_images:
                                print(f"插入选项图片: {img_path}")
                                relative_path = os.path.relpath(img_path, start=os.path.dirname(md_file_name))  # 修改为相对于.md文件的路径
                                new_lines.append(f"![图片]({relative_path}){{height=\"100px\"}}")  # 去掉上下的换行符
                                inserted_images.add(img_path)
                            else:
                                print(f"未找到匹配的选项图片: img_{question_number}_{option}_*")
                
                # 将处理后的行加入新内容
                new_lines.append(line)
            
            # 将处理后的Markdown内容写入文件
            md_file.write("\n".join(new_lines))
        
        print(f"已成功创建文件：{md_file_name}")

print("所有文件已处理完毕！")