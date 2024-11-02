import re
from docx import Document
import string


def ParseDocx(file_path):
    # 打开.docx文档
    doc = Document(file_path)
    items = []
    
    # 定义正则表达式
    code_pattern = re.compile(r'-+\s*code\s*-+')
    doc_pattern = re.compile(r'-+\s*doc\s*-+')
    section_pattern = re.compile(r'=+\s*(\d+)\s+=')  # 匹配章节格式：=== 1 ===

    current_section = None # 当前章节编号
    current_code = None
    current_doc = None

    for para in doc.paragraphs:

        # 只看"正文"，不看"标题"
        if para.style.name != 'Normal':
            continue

        text = para.text.strip()

        section_match = section_pattern.match(text)

        # 检测章节标题
        if section_match:

            # 保存上一个section的结果
            if current_section is not None:
                assert current_code is not None and current_doc is not None
                items.append((int(current_section), current_code, current_doc))

            # 获取章节编号
            current_section = section_match.group(1)
            # 清除上一章的code和doc
            current_code = None
            current_doc = None
            continue

        # 检测代码部分
        if code_pattern.match(text):
            assert current_code is None
            current_code = []
            continue

        # 检测文档部分
        if doc_pattern.match(text):
            assert current_doc is None
            current_doc = []
            continue
    
        # 提取代码中的内容
        if current_code is not None and current_doc is None:
            extracted_chars = extract_colors(para)
            current_code.extend(extracted_chars)

        # 提取文档中的内容
        if current_doc is not None:
            extracted_chars = extract_colors(para)
            current_doc.extend(extracted_chars)

    # 处理最后一个项目
    assert current_code is not None and current_doc is not None
    items.append((int(current_section),current_code,current_doc))

    return items


def extract_colors(paragraph):
    result = []
    for run in paragraph.runs:
        color = run.font.color.rgb if run.font.color else None
        color_hex = str(color) if color and str(color) != '000000' else None
        for char in run.text:
            if char in [" ", "\n", "\t", ",", "\'", "\"", "\\", "`", "\""]:
            # if char == ' ' or char == '\n' or char == '\t':
                continue

            result.append([color_hex, char])

    return result
            




if __name__ == '__main__':
    items = ParseDocx('test.docx')

    for section, code, doc in items:
        print(f"section number is: {section}")
        print("Code Characters with Colors:", code)
        print('='*50)
        print("Documentation Characters with Colors:", doc)