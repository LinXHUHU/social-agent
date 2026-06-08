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


if __name__ == "__main__":
    main()
