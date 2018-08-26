import numpy as np
from numba import jit
from matplotlib import pyplot as plt
from matplotlib import colors


@jit
def mandelbrot(z,maxiter,horizon,log_horizon):
    c = z
    for n in range(maxiter):
        az = abs(z)
        if az > horizon:
            return n - np.log(np.log(az))/np.log(2) + log_horizon
        z = z*z + c
    return 0

@jit
def mandelbrot_set(xmin,xmax,ymin,ymax,width,height,maxiter):
    horizon = 2.0 ** 40
    log_horizon = np.log(np.log(horizon))/np.log(2)
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width,height))
    for i in range(width):
        for j in range(height):
            n3[i,j] = mandelbrot(r1[i] + 1j*r2[j],maxiter,horizon, log_horizon)
    return (r1,r2,n3)


image_counter = 30

def save_image(fig):
    global image_counter
    filename = "output.png"
    image_counter += 1
    fig.savefig(filename)


@jit
def render(x,y,r,p,cmap,gamma=0.3):
    ox = x
    oy = y
    os = r

    plt.style.use('dark_background')
    dpi = 72
    img_width = 1000
    img_height = 1000
    width = 10
    height = 10
    xmin = float(x-r)
    xmax = float(x+r)
    ymin = float(y-r)
    ymax = float(y+r)

    x, y, z = mandelbrot_set(xmin, xmax, ymin, ymax, img_width, img_height, p)

    fig, ax = plt.subplots(figsize=(width, height), dpi=72)
    ticks = np.arange(0, img_width, 3 * dpi)
    x_ticks = xmin + (xmax - xmin) * ticks / img_width
    plt.xticks(ticks, x_ticks)
    y_ticks = ymin + (ymax - ymin) * ticks / img_width
    plt.yticks(ticks, y_ticks)
    ax.set_title("Mandelbrot Set: x=" + str(ox) + ", y=" + str(oy) + ", r=" + str(os) + ", colormap " + cmap)

    norm = colors.PowerNorm(gamma)
    ax.imshow(z.T, cmap=cmap, origin='lower', norm=norm)

    save_image(fig)

