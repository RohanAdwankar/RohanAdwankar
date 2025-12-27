import os
import requests
import math
USERNAME = "RohanAdwankar"
EXCLUDE_LANGS = {"HTML", "CSS"}
TOP_N = 10
BG_COLOR = "#0D1117"
TEXT_COLOR = "#C9D1D9"
COLORS_URL = "https://raw.githubusercontent.com/ozh/github-colors/master/colors.json"
def get_repos(username, token):
    repos = []
    page = 1
    headers = {"Authorization": f"token {token}"} if token else {}
    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching repos: {response.text}")
            break
        data = response.json()
        if not data:
            break
        repos.extend([r for r in data if not r['fork']]) # Only count own code
        page += 1
    return repos
def get_languages(repos, username, token):
    lang_stats = {}
    headers = {"Authorization": f"token {token}"} if token else {}
    print(f"Fetching languages for {len(repos)} repositories...")
    for i, repo in enumerate(repos):
        url = repo['languages_url']
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for lang, bytes_count in data.items():
                if lang in EXCLUDE_LANGS:
                    continue
                lang_stats[lang] = lang_stats.get(lang, 0) + bytes_count
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{len(repos)}")
    return lang_stats
def fetch_colors():
    try:
        return requests.get(COLORS_URL).json()
    except:
        return {}
def generate_svg(stats, colors_map):
    # Sort and take top N
    sorted_langs = sorted(stats.items(), key=lambda item: item[1], reverse=True)[:TOP_N]
    total_bytes = sum(stats.values()) # Total of ALL languages (excluding HTML/CSS)
    
    # Dimensions
    width = 320
    padding = 15
    col_gap = 20
    col_width = (width - (2 * padding) - col_gap) / 2
    row_height = 30
    header_height = 30
    num_rows = math.ceil(len(sorted_langs) / 2)
    height = header_height + (num_rows * row_height) + padding
    svg_content = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img">
    <title>Most Used Languages</title>
    <style>
        .header {{ font: 600 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {TEXT_COLOR}; }}
        .lang-name {{ font: 400 11px 'Segoe UI', Ubuntu, Sans-Serif; fill: {TEXT_COLOR}; }}
        .percent {{ font: 400 11px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
    </style>
    <rect x="0" y="0" width="{width}" height="{height}" rx="4.5" fill="{BG_COLOR}" stroke="#30363d" stroke-width="1"/>
    <g transform="translate({padding}, {padding})">
        <text x="0" y="10" class="header">Most Used Languages</text>
    '''
    for i, (lang, bytes_count) in enumerate(sorted_langs):
        percent = (bytes_count / total_bytes) * 100
        color = colors_map.get(lang, {}).get('color', '#8b949e') or '#8b949e'
        
        # Column 0 or 1
        col_index = 0 if i < 5 else 1
        row_index = i if i < 5 else i - 5
        x_offset = 0 if col_index == 0 else (col_width + col_gap)
        y_offset = header_height + (row_index * row_height)
        bar_width_max = col_width
        bar_width = (percent / 100) * bar_width_max
        if bar_width < 2: bar_width = 2
        svg_content += f'''
        <g transform="translate({x_offset}, {y_offset})">
            <circle cx="5" cy="6" r="4" fill="{color}"/>
            <text x="15" y="10" class="lang-name">{lang}</text>
            <text x="{col_width}" y="10" class="percent" text-anchor="end">{percent:.1f}%</text>
            <rect x="0" y="16" width="{bar_width_max}" height="4" rx="2" fill="#30363d"/>
            <rect x="0" y="16" width="{bar_width}" height="4" rx="2" fill="{color}"/>
        </g>
        '''
    svg_content += '''
    </g>
</svg>'''
    return svg_content
def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Warning: GITHUB_TOKEN not found. Rate limits may apply.")
    repos = get_repos(USERNAME, token)
    stats = get_languages(repos, USERNAME, token)
    colors = fetch_colors()
    svg = generate_svg(stats, colors)
    with open("top-langs.svg", "w") as f:
        f.write(svg)
    print("Generated top-langs.svg")
if __name__ == "__main__":
    main()
