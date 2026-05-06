import os
import re

templates_dir = r"e:\intern\local_event_finder\templates"
with open(os.path.join(templates_dir, "base.html"), "r", encoding="utf-8") as f:
    base_html = f.read()

header_part = base_html.split("{% block content %}")[0]
footer_part = base_html.split("{% endblock %}")[1]

for filename in os.listdir(templates_dir):
    if filename.endswith(".html") and filename not in ["base.html", "home.html", "fix_html.py"]:
        filepath = os.path.join(templates_dir, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"Processing {filename}...")
        
        # Check if the file is already unbroken or lacks the doubled header
        if '<main class="container">' in content:
            parts = content.split('<main class="container">')
            if len(parts) >= 2:
                # Depending on how broken it is, the core content might end differently.
                # If it's the broken format, it ends before </title> or </head> or something else.
                # All broken files we saw end their inner content just before `</title>`
                inner = parts[1]
                
                # We expect the inner content to be what's left after stripping the bad suffix
                # The bad suffix starts with `</title>` or `<title>` depending on the breakage.
                end_idx = inner.rfind('</title>')
                if end_idx != -1:
                    inner_content = inner[:end_idx].strip()
                else:
                    end_idx = inner.rfind('<!-- Google Fonts')
                    if end_idx != -1:
                        inner_content = inner[:end_idx].strip()
                    else:
                        inner_content = inner.strip()
                
                # It might have grabbed the `<main class="container">` closing tag too if it was unbroken
                # We strip `</main>` from the end if it's there
                if inner_content.endswith('</main>'):
                    inner_content = inner_content[:-7].strip()

                title = "Eventify"
                title_match = re.search(r"<title>(.*?)</title>", parts[0])
                if title_match:
                    title = title_match.group(1).strip()
                    
                clean_header = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", header_part)
                
                # rebuild
                try:
                    footer_real = footer_part.split('</main>')[1]
                except IndexError:
                    footer_real = footer_part
                    
                new_html = clean_header + inner_content + "\n    </main>\n" + footer_real
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_html)
                print(f"Repaired {filename}")
            else:
                print(f"Could not find mains for {filename}")