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

    plt.figure(figsize=(11,5))
    plt.bar(range(len(labels)), rates, tick_label=labels)
    plt.title("しりとり　単語終始比率")
    #% start: automatic generated code from pylustrator
    plt.figure(2).ax_dict = {ax.get_label(): ax for ax in plt.figure(2).axes}
    import matplotlib as mpl
    plt.figure(2).axes[0].set_position([0.074803, 0.110236, 0.885827, 0.770079])
    #% end: automatic generated code from pylustrator
    plt.show()