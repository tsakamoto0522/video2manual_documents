"""
Template rendering service using Jinja2.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from app.core import TemplateError, logger, settings
from app.models import ManualPlan


class TemplateRenderer:
    """Jinja2テンプレートレンダラー"""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize template renderer.

        Args:
            template_dir: Directory containing templates
        """
        self.template_dir = template_dir or settings.template_dir
        self.template_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,  # Markdownなので自動エスケープは無効
        )

    async def render(
        self,
        plan: ManualPlan,
        template_name: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        """
        Render manual plan to Markdown.

        Args:
            plan: Manual plan to render
            template_name: Template filename (default: manual_default.md.j2)
            output_path: Optional path to save rendered output

        Returns:
            Rendered Markdown content
        """
        template_name = template_name or settings.default_template
        logger.info(f"Rendering manual with template: {template_name}")

        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateError(f"テンプレートが見つかりません: {template_name}")

        # レンダリング用のコンテキスト
        context = {
            "title": plan.title,
            "source_video": plan.source_video,
            "created_at": plan.created_at.isoformat(),
            "steps": [step for step in plan.steps if step.selected],  # 採用されたステップのみ
        }

        # レンダリング
        content = template.render(**context)

        # 保存 (オプション)
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"Rendered manual saved to: {output_path}")

        return content

    def create_default_template(self) -> Path:
        """デフォルトテンプレートを作成 (存在しない場合)"""
        template_path = self.template_dir / settings.default_template

        if template_path.exists():
            logger.debug(f"Template already exists: {template_path}")
            return template_path

        # デフォルトテンプレートの内容
        default_content = """---
title: {{ title }}
date: {{ created_at }}
source: {{ source_video }}
---

# {{ title }}

このマニュアルは動画から自動生成されました。

---

{% for step in steps %}
## Step {{ loop.index }}: {{ step.title }}

**ナレーション:**
{{ step.narration }}

{% if step.note %}
> **注意:** {{ step.note }}
{% endif %}

{% if step.image %}
![Step {{ loop.index }}]({{ step.image }})
{% endif %}

**時間:** {{ "%.2f"|format(step.start) }}s - {{ "%.2f"|format(step.end) }}s

---

{% endfor %}

## 完了

以上で操作は完了です。
"""

        template_path.write_text(default_content, encoding="utf-8")
        logger.info(f"Default template created: {template_path}")
        return template_path
