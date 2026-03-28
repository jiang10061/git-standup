#!/usr/bin/env python3
# 这个脚本用了仅仅几天写的,能用,但别细看
import os, subprocess, argparse, re
from datetime import datetime

# --- 我随便放点东西在这里,方便以后改 ---
# 下面这俩变量现在还没用上,是给"未来高级功能"留的坑
MY_PHONE_NUMBER = "138xxxxxxxx"  # 幻想着哪天能自动给我发短信
IS_BOSS_WATCHING = False  # 如果老板在看,输出要不要拍点马屁？

# 这个字典搞了我半天,就为了几个图标
EMOJI_MAP = {
    'feat': '🌟 厉害的新功能',
    'fix': '🔧 终于修好了',
    'docs': '📖 写了点文档',
    'style': '🎨 换了个颜色',
    'refactor': '🔨 拆了重装',
    'chore': '🧹 扫地/杂事'
}

def get_config_from_file():
    """
    本来想从文件读配置,写着写着发现太麻烦,先空着吧
    """
    # 下面这行先注释掉,不然会报错,等以后有心情了再说
    # config = open("my_config.txt").read()
    return {}

def check_if_it_is_weekend():
    """
    检查是不是周末,是的话就唠叨一句
    """
    if datetime.now().weekday() >= 5:
        print("💡 喂！周末就别折腾代码了,出去玩吧！")

def find_all_my_projects(start_path):
    """
    在指定的文件夹里瞎找,看有没有 .git
    """
    result = []
    # 不敢翻太深,怕电脑卡死,就翻5层吧
    for root, dirs, files in os.walk(start_path):
        if '.git' in dirs:
            result.append(root)
            # 找到.git就别再往它里面翻了
            dirs.remove('.git')
        # 深度限制,再深不找了
        if root.count(os.sep) > 5:
            del dirs[:]
    return result

def get_git_stuff(path, since_when):
    """
    调用git命令看看这段时间干了啥
    """
    cmd = [
        'git', '-C', path, 'log',
        f'--since={since_when}',
        '--pretty=format:%s',
        '--no-merges'
    ]
    try:
        output = subprocess.check_output(cmd, text=True).strip()
        return output.split('\n') if output else []
    except:
        return []

def main():
    # 先看看今天该不该写代码
    check_if_it_is_weekend()

    parser = argparse.ArgumentParser(description="我随便写的一个站会报告小工具")
    parser.add_argument('-d', '--dir', default='.', help="你的代码在哪儿？")
    parser.add_argument('-t', '--time', default='yesterday', help="想看多久以前的？默认昨天")
    parser.add_argument('--funny', action='store_true', help="要不要加点奇怪的输出？")
    args = parser.parse_args()

    print("🚀 开始全盘搜索… 别急,喝口水…")

    all_projects = find_all_my_projects(args.dir)
    if not all_projects:
        print("😅 找了一圈,啥也没发现,你是不是走错文件夹了？")
        return

    # TODO: 这里想加个进度条,看起来会比较专业,但我还不会写
    # [进度条占位符] ########## 100%

    for proj in all_projects:
        msgs = get_git_stuff(proj, args.time)
        if msgs:
            print(f"\n📂 项目: {os.path.basename(proj)}")
            for m in msgs:
                # 试着把开头那个英文标签给换掉
                tag = m.split(':')[0].lower()
                clean_msg = m.split(':')[-1].strip()
                prefix = EMOJI_MAP.get(tag, "📌")
                print(f"  {prefix} -> {clean_msg}")

    print("\n✅ 搞定！拿去复印吧（开玩笑的）。")

    # 最后的随笔：
    # 下次想加个功能,自动把这一段发到我手机上
    # 或者自动生成一张带背景图片的日报图？
    # 算了,好累,打游戏去了。

if __name__ == "__main__":
    main()
