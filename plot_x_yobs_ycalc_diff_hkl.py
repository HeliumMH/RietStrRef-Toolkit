import argparse, sys, os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main(args, options):

    if len(args) < 2:
        print(f"Usage: <name of script>.py pattern_data_file hkl_data_file(s) <options: type -h> \n"
              f"e.g. python .\\plot_x_yobs_ycalc_diff_hkl.py pattern.txt hkl.txt -out_img_title 'My Pattern' -yfmt ln -multi_phase 1 -dpi 300 -out_img_fmt png")
        sys.exit(1)

    data_file = args[0]
    hkl_file = args[1:1+options.multi_phase]

    title = options.out_img_title if options.out_img_title else None

    df_data = pd.read_csv(data_file, sep=r'\s+', header=0, names=['x', 'yobs', 'ycalc', 'diff'])
    df_hkls=[pd.read_csv(f, sep=r'\s+', header=0, names=['d','tth', 'h', 'k', 'l']) for f in hkl_file]

    # filter non-physical noise
    mask = df_data['yobs'] > 0
    df_data = df_data[mask].copy()    

    x1 = df_data['x']
    x2 = []
    for df_hkl in df_hkls:
        mask2 = df_hkl['tth'] >= x1.min()
        mask2 &= df_hkl['tth'] <= x1.max()
        x2.append(df_hkl[mask2]['tth']) 

    # range and step for x and y axes
    if options.yfmt == 'normal':
        yobs=df_data['yobs']
        ycalc=df_data['ycalc']
        ymin = (round(min(ycalc.min(),yobs.min())/1000) - round(0.05*max(ycalc.min(),yobs.min())/1000))*1000
        ymax = (round(max(ycalc.max(),yobs.max())/1000) + round(0.05*max(ycalc.max(),yobs.max())/1000))*1000
        ystep = round((ymax - ymin) / 10 / 1000) * 1000
        label_y = r"y"
    elif options.yfmt == 'ln':
        yobs = np.log(df_data['yobs'])
        ycalc = np.log(df_data['ycalc'])
        ymin = (round(min(ycalc.min(),yobs.min())/1) - round(0.05*max(ycalc.min(),yobs.min())))*1
        ymax = (round(max(ycalc.max(),yobs.max())/1) + round(0.05*max(ycalc.max(),yobs.max())))*1
        ystep = round((ymax - ymin) / 10 / 1) * 1
        label_y = r"Lny"
    elif options.yfmt == 'sqrt':
        yobs = np.sqrt(df_data['yobs'])
        ycalc = np.sqrt(df_data['ycalc'])
        ymin = (round(min(ycalc.min(),yobs.min())/1) - round(0.1*max(ycalc.min(),yobs.min())))*1
        ymax = (round(max(ycalc.max(),yobs.max())/1) + round(0.1*max(ycalc.max(),yobs.max())))*1
        ystep = round((ymax - ymin) / 10 / 1) * 1
        label_y = r"$\sqrt{y}$"

    xmin = max((round(x1.min()/1)-1)*1, 0.5)
    xmax_ticks = [x2[jj].max() for jj in range(len(x2))]
    xmax = min((round(x1.max()/1)+1)*1, max(xmax_ticks))
    
    xstep= round((xmax - xmin) / 10 / 1) * 1
    y_min_max_step = [ ymin,  ymax,  ystep ]
    x_min_max_step = [ xmin,  xmax,  xstep ]

    # diff curve offset
    diff=yobs-ycalc
    if diff.max() > yobs.min():
        if options.yfmt == 'ln':
            diff = diff - abs(0.95*yobs.min() - diff.max())
        elif options.yfmt == 'sqrt':
            diff = diff - abs(0.5*yobs.min() - diff.max())
        elif options.yfmt == 'normal':
            diff = diff - abs(yobs.min() -0.4*ystep - diff.max())
    else:
        if abs(diff.max()-yobs.min()) > 0:
            diff = diff + (yobs.min() - 0.1*ystep - diff.max())

    # hkl ticks offset
    y2=[]
    for jj in range(len(x2)):
        offset = diff.min()-(jj+1)*0.5*ystep
        y_plot_min = offset - 0.4*ystep

        '''
        if options.yfmt == 'ln':
            offset = diff.min()-(jj+1)*0.05*abs(diff.min())
            y_plot_min = offset - 0.25*ystep
        elif options.yfmt == 'sqrt':
            offset = diff.min()-(jj+1)*1.1*abs(diff.min())
            y_plot_min = offset - 0.5*ystep
        else:
            offset = diff.min()-(jj+1)*0.4*ystep
            y_plot_min = offset - 0.4*ystep
        '''
        y2.append(np.full_like(x2[jj], offset))


    # Plot
    plt.figure(figsize=(3.3, 3.3*0.75), dpi=300)
    ax1 = plt.gca()

    plt.plot(x1, yobs, label='yobs', color='black', linewidth=0.5)
    plt.plot(x1, ycalc,label='ycalc', marker='o', markersize=1.2, markerfacecolor='none', markeredgecolor='red',markeredgewidth= 0.2, linestyle='None')
    plt.plot(x1, diff, label='diff', color='blue',  linewidth=0.5)

    # ticks
    if options.multi_phase == 1:
        plt.plot(x2[0], y2[0],   label='hkl', marker="|", markersize=3, markerfacecolor='none', markeredgecolor='green', markeredgewidth= 0.3 , linestyle='None') 
    else:
        cmap = plt.cm.get_cmap('viridis')
        for jj in range(len(x2)):
            color = cmap(jj / len(x2))
            plt.plot(x2[jj], y2[jj], label=f'HKL: {hkl_file[jj].split(".")[0]}', marker="|", markersize=3, markerfacecolor='none', markeredgecolor=color, markeredgewidth= 0.3 , linestyle='None')

    plt.xlabel('tth / deg', fontname='Arial', fontsize=7, labelpad=None)
    plt.ylabel(label_y, fontname='Arial', fontsize=7, labelpad=None)

    ax1.set_xticks(np.arange(min(0,x_min_max_step[0]), x_min_max_step[1]+x_min_max_step[2], x_min_max_step[2]))
    #ax1.set_yticks(np.arange(y_min_max_step[0], y_min_max_step[1]+y_min_max_step[2], y_min_max_step[2]))
    ax1.set_yticks([])
    ax1.tick_params(axis='x', length=2.5, width=0.5, labelsize=6, labelfontfamily = 'Arial', pad = 2) 
    
    plt.legend(fontsize=5, loc='upper right', frameon=False, title=title, title_fontsize=5)

    plt.xlim(x_min_max_step[0], x_min_max_step[1])
    plt.ylim(y_plot_min, y_min_max_step[1]) #TODO

    plt.savefig(f'{os.path.splitext(args[0])[0]}.{args_options.out_img_fmt}', 
                dpi=args_options.dpi, 
                bbox_inches='tight',
                pad_inches=0, 
                format=args_options.out_img_fmt, 
                transparent=True)
    print(f"Saved figure as {os.path.splitext(args[0])[0]}.{args_options.out_img_fmt}")  

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-yfmt', '--yfmt',
                        type=str,
                        default='normal',
                        choices=['normal', 'ln', 'sqrt'],
                        help="y-axis format, can be 'normal', 'ln' or 'sqrt'"
                        )
    parser.add_argument('-multi_phase', 
                        type=int,
                        default=1,
                        help="number of phases in the analysis"
                        )
    parser.add_argument('-dpi', 
                        type=int,
                        default=300,
                        help="DPI for the saved figure, default 300"
                        )
    parser.add_argument('-out_img_fmt',
                        type=str,
                        default='jpg',
                        choices=['jpg', 'png', 'svg'],
                        help="Output image format, default 'jpg'"
                        )
    parser.add_argument('-out_img_title',
                        type=str,
                        default=None,
                        help="Title for the output image"
                        )
    
    args_options, sysargs = parser.parse_known_args()

    main(sysargs, args_options)
