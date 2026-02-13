import pandas as pd
import matplotlib.pyplot as plt

class ResultVisualizer:

    def visualize_boxplot(self):
        file_path = "result_heap_size_decentral2.csv"
        file_path2 = "result_heap_size_central.csv"

        df = pd.read_csv(file_path)
        df2 = pd.read_csv(file_path2)
        combined_frame = pd.concat([df, df2], axis=1, ignore_index=True)
        plot_data = []
        plot_labels = []
        colors=[]
        for col in df.columns:
            plot_data.append(df[col].dropna())
            plot_labels.append(f"D1: {col}")
            colors.append('skyblue')  # Farbe für Datei 1

        for col in df2.columns:
            plot_data.append(df2[col].dropna())
            plot_labels.append(f"D2: {col}")
            colors.append('lightgreen')

        bplot = plt.boxplot(plot_data, labels=plot_labels, patch_artist=True, notch=False, showfliers=True)

        for patch, color in zip(bplot['boxes'], colors):
            patch.set_facecolor(color)
        #plt.figure()
        plt.title("Boxplot der Zeitreihe")
        plt.yscale("log")
        plt.ylabel("Werte")
        plt.show()


if __name__ == '__main__':
    ResultVisualizer().visualize_boxplot()