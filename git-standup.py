#!/usr/bin/env python3
# 这个脚本虽然功能变强了，但依然是我在摸鱼时间拼凑出来的，别细看。
import os, subprocess, argparse, sys
from datetime import datetime

# --- 依然是这些还没用的坑，留着显得我很有远见 ---
MY_PHONE_NUMBER = "138xxxxxxxx" 
IS_BOSS_WATCHING = False 

# 这里的字典是我翻烂了手册才凑齐的
EMOJI_MAP = {
    'feat': '🌟 厉害的新功能',
    'fix': '🔧 终于修好了',
    'docs': '📖 写了点文档',
    'style': '🎨 换了个颜色',
    'refactor': '🔨 拆了重装',
    'chore': '🧹 扫地/杂事'
}

def check_if_it_is_weekend(is_en):
    """检查是不是周末，是的话就唠叨一句"""
    if datetime.now().weekday() >= 5:
        msg = "💡 Hey! Weekend! Go out and play!" if is_en else "💡 喂！周末就别折腾代码了,出去玩吧！"
        print(msg)

def find_all_my_projects(start_path, ignore_list=None):
    """在文件夹里瞎找 .git，但我学会了躲开那些讨厌的文件夹"""
    result = []
    ignore_list = ignore_list or []
    start_path = os.path.abspath(start_path)
    
    for root, dirs, files in os.walk(start_path):
        # 如果这个文件夹在黑名单里，赶紧溜
        if any(ign in root for ign in ignore_list):
            continue
            
        if '.git' in dirs:
            result.append(root)
            dirs.remove('.git')
            
        # 深度限制，再深电脑真的要炸了
        if root.count(os.sep) - start_path.count(os.sep) > 3:
            del dirs[:]
    return result

def get_git_stuff(path, since_when, author=None, branch=None, exclude=None):
    """调用git命令看看到底干了啥，支持过滤掉一些垃圾提交"""
    cmd = ['git', '-C', path, 'log', f'--since={since_when}', '--pretty=format:%s', '--no-merges']
    
    if author: cmd.append(f'--author={author}')
    if branch: cmd.append(branch)
    
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
        if not output: return []
        
        lines = output.split('\n')
        # 如果提交信息里包含我想屏蔽的词（比如 wip），就当没看见
        if exclude:
            lines = [l for l in lines if not any(word.lower() in l.lower() for word in exclude)]
        return lines
    except:
        return []

def main():
    # 看看是不是要英文版，毕竟有时候要装个国际化大牛
    is_en = '--help-en' in sys.argv
    
    # 构建一个超级详细的帮助文档
    help_desc = "🚀 Git Standup: 一个帮你从乱七八糟的提交里刨出日报的小工具"
    if is_en: help_desc = "🚀 Git Standup: Get your daily report without breaking a sweat."

    usage_examples = """
使用示例 (Examples):
  python git-standup.py -d ~/work -t yesterday                # 默认用法
  python git-standup.py -t 3d --author "YourName"             # 看自己前三天的活
  python git-standup.py --table --output report.md           # 生成表格并存到文件
  python git-standup.py -x wip temp test                      # 过滤掉那些见不得人的提交
    """

    parser = argparse.ArgumentParser(
        description=help_desc,
        epilog=usage_examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 这里把参数分个类，显得我写代码很专业
    basic_args = parser.add_argument_group('基础设置' if not is_en else 'Basic Settings')
    basic_args.add_argument('-d', '--dir', default='.', help="从哪儿开始找项目？")
    basic_args.add_argument('-t', '--time', default='yesterday', help="时间跨度 (如: 1d, 1w, yesterday)")
    basic_args.add_argument('-a', '--author', help="只看谁写的？(支持模糊匹配)")
    
    filter_args = parser.add_argument_group('过滤选项' if not is_en else 'Filter Options')
    filter_args.add_argument('-b', '--branch', help="指定分支名，不写就看当前的")
    filter_args.add_argument('-x', '--exclude', nargs='+', help="排除包含这些词的提交 (如: wip temp)")
    filter_args.add_argument('--ignore', nargs='+', help="忽略包含这些词的文件夹")
    
    out_args = parser.add_argument_group('输出控制' if not is_en else 'Output Control')
    out_args.add_argument('--table', action='store_true', help="直接输出 Markdown 表格格式")
    out_args.add_argument('-o', '--output', help="把结果存到这个文件里")
    out_args.add_argument('--help-en', action='store_true', help="Show help message in English")

    args = parser.parse_args()
    check_if_it_is_weekend(is_en)

    print("🚀 正在全盘搜索... 别急，代码正在努力跑..." if not is_en else "🚀 Searching... please wait...")

    all_projects = find_all_my_projects(args.dir, args.ignore)
    results = []
    stats = {k: 0 for k in EMOJI_MAP.keys()}
    stats['other'] = 0

    for proj in all_projects:
        msgs = get_git_stuff(proj, args.time, args.author, args.branch, args.exclude)
        if msgs:
            proj_name = os.path.basename(proj)
            for m in msgs:
                parts = m.split(':', 1)
                tag = parts[0].lower() if len(parts) > 1 else 'other'
                content = parts[1].strip() if len(parts) > 1 else m
                
                emoji_tag = EMOJI_MAP.get(tag, '📌 其他')
                if tag in stats: stats[tag] += 1
                else: stats['other'] += 1
                
                results.append({'proj': proj_name, 'tag': emoji_tag, 'msg': content})

    if not results:
        print("😅 找了一圈啥也没有，你昨天是不是偷懒了？" if not is_en else "😅 Nothing found. Did you even work?")
        return

    # 开始攒报告内容
    report_lines = []
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    if args.table:
        report_lines.append(f"### 📅 日报 ({date_str})\n")
        report_lines.append("| 项目 | 类型 | 内容 |")
        report_lines.append("| :--- | :--- | :--- |")
        for r in results:
            report_lines.append(f"| {r['proj']} | {r['tag']} | {r['msg']} |")
    else:
        report_lines.append(f"📢 Git 站会回执 ({date_str})\n" + "="*40)
        curr_p = ""
        for r in results:
            if r['proj'] != curr_p:
                curr_p = r['proj']
                report_lines.append(f"\n📂 项目: {curr_p}")
            report_lines.append(f"  {r['tag']} -> {r['msg']}")

    # 把统计摘要也塞进去
    report_lines.append("\n" + "-"*40)
    report_lines.append("📊 工作量统计 (Summary):")
    for tag, count in stats.items():
        if count > 0:
            label = EMOJI_MAP.get(tag, "📌 其他记录")
            report_lines.append(f"  {label}: {count}")

    final_content = "\n".join(report_lines)
    print("\n" + final_content)

    # 导出到文件，省得手动复制了
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"\n✅ 报告已存档到: {args.output}")
        except Exception as e:
            print(f"\n❌ 存档失败了，可能文件夹不让写: {e}")

    print("\n✅ 任务完成！去交差吧，我要去打游戏了。" if not is_en else "\n✅ Done! Time to play games.")

if __name__ == "__main__":
    main()
