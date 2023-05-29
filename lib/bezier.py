# Thanks unutbu!
# https://stackoverflow.com/questions/246525/how-can-i-draw-a-bezier-curve-using-pythons-pil

def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = _pascal_row(n-1)
    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result
    return bezier

def _pascal_row(n, memo={}):
    # This returns the nth row of Pascal's Triangle
    if n in memo:
        return memo[n]
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n//2+1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n&1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    memo[n] = result
    return result

##############################################################################

if __name__ == '__main__':
    from PIL import Image
    from PIL import ImageDraw

    im = Image.new('RGBA', (100, 100), (0, 0, 0, 0)) 
    draw = ImageDraw.Draw(im)
    ts = [t/100.0 for t in range(101)]

    xys = [(50, 100), (80, 80), (100, 50)]
    bezier = make_bezier(xys)
    points = bezier(ts)

    xys = [(100, 50), (100, 0), (50, 0), (50, 35)]
    bezier = make_bezier(xys)
    points.extend(bezier(ts))

    xys = [(50, 35), (50, 0), (0, 0), (0, 50)]
    bezier = make_bezier(xys)
    points.extend(bezier(ts))

    xys = [(0, 50), (20, 80), (50, 100)]
    bezier = make_bezier(xys)
    points.extend(bezier(ts))

    draw.polygon(points, fill = 'red')   
    im.show() 