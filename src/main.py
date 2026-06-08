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

    p = engine.create(name, initial={
        "basic": {"name": name, "relationship": relationship}
    })

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


if __name__ == "__main__":
    main()
