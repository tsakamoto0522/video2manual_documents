"""
PDF export service.
"""
import asyncio
from pathlib import Path
from typing import Optional

from app.core import ExportError, logger, settings


class PDFExporter:
    """PDF エクスポーター"""

    def __init__(self, engine: Optional[str] = None):
        """
        Initialize PDF exporter.

        Args:
            engine: PDF engine to use (playwright or weasyprint)
        """
        self.engine = engine or settings.pdf_engine

    async def markdown_to_pdf(self, markdown_path: Path, output_path: Path) -> Path:
        """
        Convert Markdown to PDF.

        Args:
            markdown_path: Path to Markdown file
            output_path: Path to output PDF file

        Returns:
            Path to generated PDF file
        """
        logger.info(f"Converting Markdown to PDF using {self.engine}")

        if self.engine == "playwright":
            return await self._convert_with_playwright(markdown_path, output_path)
        elif self.engine == "weasyprint":
            return await self._convert_with_weasyprint(markdown_path, output_path)
        else:
            raise ExportError(f"Unknown PDF engine: {self.engine}")

    async def _convert_with_playwright(self, markdown_path: Path, output_path: Path) -> Path:
        """Playwright を使用して PDF に変換"""
        try:
            from playwright.async_api import async_playwright
            import markdown
            import base64
            import re

            # Markdown を HTML に変換
            md_content = markdown_path.read_text(encoding="utf-8")

            # 画像パスを Base64 データ URI に変換
            def replace_image_with_base64(match):
                alt_text = match.group(1)
                img_path_str = match.group(2)

                logger.info(f"Processing image path: {img_path_str}")

                # パスを正規化
                img_path = Path(img_path_str)

                # 'data/' で始まる相対パスの場合
                if img_path_str.startswith('data/'):
                    # settings.data_dir の親ディレクトリからの相対パスとして解決
                    img_path = Path.cwd() / img_path_str
                # 絶対パスでない場合
                elif not img_path.is_absolute():
                    img_path = settings.data_dir / img_path_str.lstrip('./')

                logger.info(f"Resolved image path: {img_path}, exists: {img_path.exists()}")

                if img_path.exists():
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            # 画像の拡張子から MIME タイプを判定
                            ext = img_path.suffix.lower()
                            mime_type = {
                                '.jpg': 'image/jpeg',
                                '.jpeg': 'image/jpeg',
                                '.png': 'image/png',
                                '.gif': 'image/gif',
                            }.get(ext, 'image/jpeg')
                            return f'![{alt_text}](data:{mime_type};base64,{img_data})'
                    except Exception as e:
                        logger.warning(f"Failed to encode image {img_path}: {e}")

                return match.group(0)  # 失敗した場合は元のまま

            # Markdown内の画像参照を Base64 に変換
            md_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_with_base64, md_content)

            html_content = markdown.markdown(
                md_content,
                extensions=["fenced_code", "tables", "nl2br"],
            )

            # スタイル付き HTML を作成
            full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: "Segoe UI", "Hiragino Sans", "Meiryo", sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            margin: 10px 0;
        }}
        h1, h2, h3 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 5px;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin-left: 0;
            padding-left: 15px;
            color: #666;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

            # Playwright で PDF 生成
            output_path.parent.mkdir(parents=True, exist_ok=True)

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.set_content(full_html)
                await page.pdf(
                    path=str(output_path),
                    format="A4",
                    margin={
                        "top": "20mm",
                        "right": "20mm",
                        "bottom": "20mm",
                        "left": "20mm",
                    },
                )
                await browser.close()

            logger.info(f"PDF generated with Playwright: {output_path}")
            return output_path

        except ImportError as e:
            raise ExportError(
                f"Playwright not installed. Run: pip install playwright && playwright install"
            )
        except Exception as e:
            logger.error(f"Playwright PDF export failed: {e}")
            raise ExportError(f"PDF 生成に失敗しました: {e}")

    async def _convert_with_weasyprint(self, markdown_path: Path, output_path: Path) -> Path:
        """WeasyPrint を使用して PDF に変換"""
        try:
            import markdown
            from weasyprint import HTML

            # Markdown を HTML に変換
            md_content = markdown_path.read_text(encoding="utf-8")
            html_content = markdown.markdown(
                md_content,
                extensions=["fenced_code", "tables", "nl2br"],
            )

            # PDF 生成
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 非同期実行
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: HTML(string=html_content).write_pdf(str(output_path)),
            )

            logger.info(f"PDF generated with WeasyPrint: {output_path}")
            return output_path

        except ImportError:
            raise ExportError("WeasyPrint not installed. Run: pip install weasyprint")
        except Exception as e:
            logger.error(f"WeasyPrint PDF export failed: {e}")
            raise ExportError(f"PDF 生成に失敗しました: {e}")
