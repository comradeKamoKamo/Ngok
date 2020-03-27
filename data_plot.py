import numpy as np
from matplotlib import pyplot as plt
import pickle
import matplotlib
from matplotlib.font_manager import FontProperties
from matplotlib.colors import Normalize

# now import pylustrator
import pylustrator

if __name__=="__main__":
    
    
    # activate pylustrator
    pylustrator.start()

    # 単語ヒートマップ

    cm = np.load("cm.npy")
    labels = []
    chars = pickle.load(open("endList.pickle","rb"))
    for char in chars:
        char = char[0]
        a = sorted(char)[0]
        labels.append(a)

    # ゴミを除去
    trashes = [labels.index("ッ"), labels.index("ヱ"), labels.index("ヰ")]
    labels.remove("ッ")
    labels.remove("ヱ")
    labels.remove("ヰ")
    cm = np.delete(cm, obj=trashes, axis=1)
    cm = np.delete(cm, obj=trashes, axis=0)
    np.save("cm_clean.npy",cm)
    trashes = sorted(trashes)
    for i, t in enumerate(trashes):
        chars.pop(t - i)
    pickle.dump(chars, open("endList_clean.pickle","wb"))

    font_path = "/usr/share/fonts/windows/meiryo.ttc"
    font_prop = FontProperties(fname=font_path)
    matplotlib.rcParams["font.family"] = font_prop.get_name()

    fig = plt.figure(figsize=(11, 11))
    ax = plt.subplot()
    cax = ax.matshow(cm, interpolation="nearest", cmap="jet", norm=Normalize(vmin=0, vmax=5000))
    fig.colorbar(cax)
    ys, xs = np.meshgrid(range(cm.shape[0]),range(cm.shape[1]),indexing="ij")
    plt.xticks(xs[0,:], labels)
    plt.yticks(ys[:,0], labels)  
    plt.title("しりとり　単語ヒートマップ")
    plt.xlabel("終端文字")
    plt.ylabel("先頭文字")

    # 単語終始比率
    first_sums = cm.sum(axis=1)
    end_sums = cm.sum(axis=0)
    rates = end_sums / first_sums

    plt.figure()
    plt.bar(range(len(labels)), rates, tick_label=labels)
    plt.title("しりとり　単語終始比率")
    #% start: automatic generated code from pylustrator
    plt.figure(2).ax_dict = {ax.get_label(): ax for ax in plt.figure(2).axes}
    import matplotlib as mpl
    plt.figure(2).axes[0].patches[0].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[1].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[2].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[3].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[4].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[5].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[6].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[7].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[8].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[9].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[10].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[11].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[12].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[13].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[14].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[15].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[16].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[17].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[18].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[19].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[20].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[21].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[22].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[23].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[24].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[25].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[26].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[27].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[28].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[29].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[30].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[31].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[32].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[33].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[34].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[35].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[36].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[37].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[38].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[39].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[40].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[41].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[42].set_facecolor("#ff0000")
    plt.figure(2).axes[0].patches[43].set_facecolor("#ff0000")
    plt.figure(2).text(0.5, 0.5, 'New Text', transform=plt.figure(2).transFigure)  # id=plt.figure(2).texts[0].new
    #% end: automatic generated code from pylustrator
    plt.show()