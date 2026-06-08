"""Social Coach — AI-powered social interaction coach."""
import json
import os
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.persona.engine import PersonaEngine
from src.persona import storage

console = Console()
engine = PersonaEngine()


@click.group()
def main():
    """AI 社交指导助手"""
    pass


@main.group()
def persona():
    """人物画像管理"""
    pass


@persona.command()
@click.option("--name", prompt="姓名", help="对方姓名")
@click.option("--relationship", prompt="关系（同事/朋友/暧昧对象/长辈/陌生人等）",
              default="陌生人")
def add(name, relationship):
    """交互式创建画像"""
    from rich.prompt import Prompt

    p = engine.create(name)
    p.basic.relationship = relationship
    from datetime import datetime
    p.updated_at = datetime.now().isoformat()
    storage.save(p)

    if click.confirm("是否现在完善画像?"):
        goal = Prompt.ask("  你对此人的目标", default="")
        attitude = Prompt.ask("  此人对你的态度", default="")
        if goal or attitude:
            p.goals.my_goal = goal
            p.goals.their_attitude = attitude
            from datetime import datetime
            p.updated_at = datetime.now().isoformat()
            storage.save(p)

    console.print(f"\n[green]✓ 画像已创建: {p.persona_id}[/green]")
    console.print(f"  存储位置: ~/.social-agent/personas/{p.persona_id}.json")


@persona.command()
@click.argument("persona_id")
def show(persona_id):
    """查看画像详情"""
    p = engine.get(persona_id)
    console.print(f"\n[bold cyan]━━━ {p.basic.name} ({p.persona_id}) ━━━[/bold cyan]")
    console.print(f"  关系: {p.basic.relationship} | 亲密度: {p.basic.closeness}/10")
    traits_str = ', '.join(t.trait for t in p.personality.traits) or '(无)'
    console.print(f"  性格特征: {traits_str}")
    console.print(f"  沟通风格: {p.personality.communication_style or '(未知)'}")
    console.print(f"  安全话题: {', '.join(p.strategies.topics_to_use) or '(无)'}")
    console.print(f"  禁忌话题: {', '.join(p.strategies.topics_to_avoid) or '(无)'}")
    console.print(f"  目标: {p.goals.my_goal or '(未设定)'}")
    console.print(f"\n完整JSON: ~/.social-agent/personas/{persona_id}.json")


@persona.command()
def list():
    """列出所有画像"""
    personas = engine.list_all()
    if not personas:
        console.print("[dim]还没有任何画像，使用 persona add 创建[/dim]")
        return

    table = Table(title="人物画像列表")
    table.add_column("ID", style="cyan")
    table.add_column("姓名", style="bold")
    table.add_column("关系")
    table.add_column("亲密度")
    table.add_column("目标")

    for p in personas:
        goal = p.goals.my_goal[:20] + "..." if len(p.goals.my_goal) > 20 else p.goals.my_goal
        table.add_row(
            p.persona_id, p.basic.name, p.basic.relationship,
            str(p.basic.closeness), goal
        )
    console.print(table)


@persona.command()
@click.argument("persona_id")
@click.option("--field", "-f", default=None, help="字段路径，如 goals.my_goal")
@click.option("--value", "-v", default=None, help="新值")
def edit(persona_id, field, value):
    """编辑画像。不加参数则打开JSON文件直接编辑。"""
    if not field:
        editor = os.environ.get("EDITOR", "vim")
        config_path = Path.home() / ".social-agent" / "personas" / f"{persona_id}.json"
        subprocess.call([editor, str(config_path)])
        console.print(f"[green]✓ 请用编辑器修改 {config_path}[/green]")
        return
    p = engine.get(persona_id)
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        parsed = value
    parts = field.split(".")
    obj = p
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], parsed)
    from datetime import datetime
    p.version += 1
    p.updated_at = datetime.now().isoformat()
    storage.save(p)
    console.print(f"[green]✓ 已更新 {persona_id} 的 {field}[/green]")


@persona.command()
def me_show():
    """查看自己的画像"""
    from src.self_profile import load as load_self
    p = load_self()
    console.print(f"\n[bold cyan]━━━ 自我画像 ━━━[/bold cyan]")
    console.print(f"  姓名: {p.name}")
    traits_str = ', '.join(p.personality.traits) or '(未设定)'
    console.print(f"  性格特征: {traits_str}")
    console.print(f"  沟通风格: {p.personality.communication_style or '(未设定)'}")
    phrases_str = ', '.join(p.personality.catchphrases) or '(无)'
    console.print(f"  常用口头禅: {phrases_str}")
    console.print(f"  价值观: {', '.join(p.personality.values) or '(未设定)'}")
    console.print(f"\n文件位置: ~/.social-agent/self.json")


@persona.command()
@click.option("--field", "-f", default=None, help="字段路径，如 personality.communication_style")
@click.option("--value", "-v", default=None, help="新值")
def me_edit(field, value):
    """编辑自己的画像。不加参数则打开JSON文件直接编辑。"""
    from src.self_profile import load as load_self, save as save_self
    if not field:
        editor = os.environ.get("EDITOR", "vim")
        config_path = Path.home() / ".social-agent" / "self.json"
        subprocess.call([editor, str(config_path)])
        console.print(f"[green]✓ 请用编辑器修改 {config_path}[/green]")
        return
    p = load_self()
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        parsed = value
    parts = field.split(".")
    obj = p
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], parsed)
    save_self(p)
    console.print(f"[green]✓ 已更新自己的画像: {field}[/green]")


@main.group()
def coach():
    """教练指导"""
    pass


@coach.command()
@click.argument("persona_id")
@click.option("--scene", "-s", default="", help="场景描述，如'公司茶水间'")
def strategy(persona_id, scene):
    """见面前的策略分析"""
    from src.coach.engine import CoachEngine
    p = engine.get(persona_id)
    ce = CoachEngine()
    console.print(f"\n[bold cyan]分析 {p.basic.name}...[/bold cyan]")
    result = ce.advise_strategy(p, scene)
    console.print(Panel(result, title="策略建议", border_style="green"))


@coach.command()
@click.argument("persona_id")
def live(persona_id):
    """进入实时指导交互模式（文本模拟）"""
    from src.coach.engine import CoachEngine
    p = engine.get(persona_id)
    ce = CoachEngine()

    console.print(f"\n[bold cyan]📋 已加载画像：{p.basic.name}（{p.basic.relationship}）[/bold cyan]")
    if p.goals.my_goal:
        console.print(f"[dim]🎯 当前目标：{p.goals.my_goal}[/dim]")

    result = ce.advise_strategy(p, "文本聊天")
    console.print(Panel(result, title="💡 建议策略", border_style="green"))

    console.print("\n[dim][输入对方说的话，或 /help 查看命令][/dim]\n")

    context: list[str] = []

    while True:
        try:
            user_input = click.prompt("> ", prompt_suffix="")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]已退出[/dim]")
            break

        user_input = user_input.strip()
        if user_input.lower() in ("/exit", "/quit", "/q"):
            break
        elif user_input.startswith("/warmup"):
            result = ce.advise_warmup(p, context)
            console.print(Panel(result, title="🧊 暖场话题", border_style="yellow"))
            continue
        elif user_input.startswith("/help"):
            console.print("""[bold]可用命令:[/bold]
  <任意文本>     输入对方说的话，AI 分析 + 给话术建议
  /warmup        手动请求暖场话题
  /exit, /q      退出
  Ctrl+C         退出""")
            continue
        elif not user_input:
            continue

        context.append(user_input)

        analysis = ce.advise_analysis(p, user_input, context[:-1])
        console.print(Panel(analysis, title="🤔 分析", border_style="blue"))

        reply = ce.advise_reply(p, context)
        console.print(Panel(reply, title="💬 回复建议", border_style="green"))


@coach.command()
@click.argument("persona_id")
def warmup(persona_id):
    """手动请求暖场话题"""
    from src.coach.engine import CoachEngine
    p = engine.get(persona_id)
    ce = CoachEngine()
    result = ce.advise_warmup(p)
    console.print(Panel(result, title="🧊 暖场话题", border_style="yellow"))


@main.group()
def analyze():
    """对话分析"""
    pass


@analyze.command()
@click.argument("text_file")
@click.option("--persona-id", "-p", default=None, help="关联的人物画像ID")
def text(text_file, persona_id):
    """分析对话文本文件"""
    from pathlib import Path
    from src.analyzer.engine import Analyzer
    from src.analyzer.merger import merge_updates

    content = Path(text_file).read_text()
    persona = engine.get(persona_id) if persona_id else None

    console.print("[bold]正在分析对话...[/bold]")
    analyzer_obj = Analyzer()
    result = analyzer_obj.analyze(content, persona)

    report = result.get("report", result)
    console.print(Panel(str(report), title="📊 分析报告", border_style="blue"))

    updates = analyzer_obj.suggest_updates(result)
    if updates and persona:
        console.print(f"\n[yellow]发现 {len(updates)} 条画像更新建议[/yellow]")
        for i, u in enumerate(updates):
            console.print(f"  [{i+1}] {u['field']} ← {u.get('value', '')}")

        if click.confirm("是否应用这些更新?"):
            updated, conflicts = merge_updates(persona, updates)
            from datetime import datetime
            updated.version = persona.version + 1
            updated.updated_at = datetime.now().isoformat()
            from src.persona import storage
            storage.save(updated)
            console.print(f"[green]✓ 画像已更新[/green]")
            for c in conflicts:
                console.print(f"  [yellow]⚠ {c['reason']}[/yellow]")


@analyze.command()
@click.argument("image_path")
@click.option("--persona-id", "-p", default=None, help="关联的人物画像ID")
def screenshot(image_path, persona_id):
    """分析聊天截图"""
    from src.utils.screenshot import extract_text
    from src.analyzer.engine import Analyzer

    console.print("[bold]正在识别截图中的对话...[/bold]")
    text_content = extract_text(image_path)
    console.print(f"[dim]识别结果:[/dim]\n{text_content}\n")

    persona = engine.get(persona_id) if persona_id else None
    analyzer_obj = Analyzer()
    result = analyzer_obj.analyze(text_content, persona)

    report = result.get("report", result)
    console.print(Panel(str(report), title="📊 分析报告", border_style="blue"))


@main.group()
def knowledge():
    """社交知识库管理"""
    pass


@knowledge.command()
def list():
    """列出所有原则"""
    from src.knowledge.base import KnowledgeBase
    kb = KnowledgeBase()
    principles = kb.list_all()
    console.print(f"\n共 {len(principles)} 条原则:\n")
    for p in principles:
        console.print(f"[cyan]{p.principle_id}[/cyan] [{p.source_title}] {p.principle}")
        console.print(f"  场景: {', '.join(p.applicable_scenarios)}")


@knowledge.command()
@click.argument("query")
def search(query):
    """搜索原则"""
    from src.knowledge.base import KnowledgeBase
    kb = KnowledgeBase()
    results = kb.search(scene_labels=[query], limit=5)
    if not results:
        results = kb.search(scene_labels=["通用社交"], limit=3)
    for p in results:
        console.print(Panel(
            f"[bold]{p.principle}[/bold]\n来源: {p.source_title}\n做法: {p.how_to_apply}",
            title=p.principle_id
        ))


@knowledge.command()
@click.option("--principle", prompt="原则内容")
@click.option("--source", prompt="来源书名")
@click.option("--category", prompt="分类", default="通用社交")
def add(principle, source, category):
    """手动添加原则"""
    from src.knowledge.base import KnowledgeBase
    kb = KnowledgeBase()
    pid = kb.add({
        "principle_id": f"user_{len(kb.list_all()) + 1:03d}",
        "source_type": "manual",
        "source_title": source,
        "principle": principle,
        "category": category,
        "applicable_scenarios": [],
        "how_to_apply": "",
        "counter_example": "",
    })
    console.print(f"[green]✓ 已添加: {pid}[/green]")


if __name__ == "__main__":
    main()
