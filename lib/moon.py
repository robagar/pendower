from math import radians, pi, sin, cos

fill = 'white'
outline = 'black'

new_moon_fill = 'black'
new_moon_outline = 'white'

def draw_moon(draw, center_xy, radius, phase, rotation_degrees):
    rotation = radians(rotation_degrees)
    if phase > 0.5:
        rotation = -rotation

    def transform(ps):
        return list(map(lambda p: translate(center_xy, scale(radius, rotate(rotation, p))), ps))

    def draw_polygon(ps):
        draw.polygon(transform(ps), fill=fill, outline=outline)

    def transform_no_rotation(ps):
        return list(map(lambda p: translate(center_xy, scale(radius, p)), ps))

    box = transform_no_rotation([(-1,-1), (1,1)])

    if phase == 0 or phase == 1:
        # new moon
        print(f"[moon] NEW {phase}")
        draw.ellipse(box, fill=new_moon_fill, outline=new_moon_outline)

    elif phase < 0.5:
        # waxing  
        print(f"[moon] WAXING {phase}")
        ps = []
        
        # limb
        for t in range(0, 180, 5):
            a = radians(t)
            ps.append((sin(a), cos(a)))

        # terminator
        m = terminator_minor_axis(phase)
        for t in range(180, 0, -5):
            a = radians(t)
            ps.append((m * sin(a), cos(a)))    

        draw_polygon(ps)   

    elif phase == 0.5:
        # full
        print(f"[moon] FULL {phase}")
        draw.ellipse(box, fill=fill, outline=outline)

    else:
        # waning
        print(f"[moon] WANING {phase}")
        ps = []

        # terminator
        m = terminator_minor_axis(phase)
        for t in range(360, 180, -5):
            a = radians(t)
            ps.append((m * sin(a), cos(a)))    
        
        # limb
        for t in range(180, 360, 5):
            a = radians(t)
            ps.append((sin(a), cos(a)))

        draw_polygon(ps)  

def terminator_minor_axis(phase):
    a = 2 * pi * phase
    return cos(a)

def rotate(angle, p):
    (x,y) = p
    c = cos(angle)
    s = sin(angle)
    return(x * c - y * s, x * s + y * c)

def scale(scale, p):
    return (p[0] * scale, p[1] * scale)

def translate(delta, p):
    return (p[0] + delta[0], p[1] + delta[1])


if __name__ == "__main__":
    from PIL import Image,ImageDraw

    radius = 100
    d = radius * 2

    n = 24

    w = n * (d + 20) + 20
    h = d + 40
    image = Image.new('RGBA', (w, h), 'rgba(0,0,0,0)')

    draw = ImageDraw.Draw(image)

    x = radius + 20
    y = radius + 20
    for i in range(n):
        phase = i/n
        # draw.text((x, 0), f'{phase:.2f}', fill='black', anchor='ma')        
        draw_moon(draw, (x, y), radius, phase, 48) 
        x += d + 20

    image.show()
