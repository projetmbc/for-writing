#!/usr/bin/env python3

# ------------------- #
# -- CSS FUNCTIONS -- #
# ------------------- #

def normalize_rgb(rgb):
    return map(
        lambda c: int(c*255),
        rgb
    )


def generate_gradient_css(colors):
    rgb_points = []

    for c in colors:
        r, g, b = normalize_rgb(c)
        rgb_points.append(f"rgb({r},{g},{b})")

    css_points = ', '.join(rgb_points)
    css_code   = f"linear-gradient(to right, {css_points})"

    return css_code


def generate_discrete_grid(colors, border_color):
    """Grille de carrés : Taille fixe 45px (identique hauteur spectre)"""
    html = '''
    <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;
                max-width: 500px; align-items: flex-start;">'''
    for c in colors:
        r, g, b = normalize_rgb(c)
        html += f'''
            <div style="
                width: 45px;
                height: 45px;
                flex: 0 0 45px;
                background: rgb({r},{g},{b});
                border-radius: 4px;
                border: 1px solid {border_color};">
            </div>'''
    html += '</div>'
    return html
