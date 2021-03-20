'''
Input file: /result/raw/[Parti_Name]/behavioral/
Output file (Data): /result/curve_fitting/data/
Output file (Graph): /result/curve_fitting/graph/
Result file: ../../part2_result/
#
The script will read the raw behavioral result from the raw directory,
return unmerged file for each participants on psychometric curve, in data directory,
also return graph for each conditions for each participants in graph directory.
'''

from scipy.optimize import minimize
from scipy.stats import norm
import csv
import matplotlib
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pathlib
import pingouin as pg
import sys


def manage_path():
    #  in
    current_path = pathlib.Path(__file__).parent.absolute()
    raw_path = current_path / 'raw_save'
    parti_path_array = [x / 'behavioral' for x in raw_path.iterdir() if x.is_dir()]

    #  out
    out_data_path = current_path / 'fitted_data'
    out_graph_path = current_path / 'fitted_graph'
    pathlib.Path(out_data_path).mkdir(parents=True, exist_ok=True)
    pathlib.Path(out_graph_path).mkdir(parents=True, exist_ok=True)

    return parti_path_array, out_data_path, out_graph_path


def read_files(master, sessions):
    #  Read Trial Info
    master = master[0]
    master = pd.read_csv(master, 'r', delimiter=',')

    #  Read Eprime session response files
    for i in range(6):
        session = sessions[i]
        session = pd.read_table(session, 'r', delimiter='\t', header=[1], encoding='utf-16')
        if i == 0:
            merged = session
        else:
            merged = pd.concat([merged, session], ignore_index = True)

    #  Return Response and append it to master
    resp = merged['Response.RESP']
    master['Resp'] = resp
    master['Resp'] = master['Resp'].replace(to_replace=['f', 'j'], value=[0, 1])
    return master


def preprocess(master):
    #  setup
    con1 = []
    con2 = []
    con3 = []
    condition = []
    np.array(condition)
    for names in [con1, con2, con3]:
        condition.append(names)
        np.array(names)

    orientations = [-30,-20, -10, 0, 10, 20, 30]
    ori_frame = []

    count1 = []
    count2 = []
    count3 = []
    count = []
    for names in [count1, count2, count3]:
        count.append(names)
        np.array(names)

    #  sort by condition and orientation then sum response 'j'
    for i in range(3):
        condition[i] = master[master.Condition == (i+1)]
        for ori in orientations:
            ori_frame = condition[i][condition[i].Orientation == ori]
            count[i].append(ori_frame['Resp'].sum(axis = 0))

    #  retrieve info
    info = [master.Parti_No[0], master.Parti_Name[0]]

    return count, info


def fit(for_fit, parti_no, graph_path):
    #  Setup output
    alpha_array = []
    beta_array = []
    success_array = []
    r_square_array = []
    fit_result = [alpha_array,
                  beta_array,
                  success_array,
                  r_square_array]

    #  Setup data
    xdata = np.arange(-30, 31, 10)
    for i in range(3):
        ydata = for_fit[i]
        ydata = [y / 36 for y in ydata]

        #  fitting
        def gauss(params):
            beta = params[0]
            alpha = params[1]
            yPred = norm.cdf(xdata, loc=alpha, scale=beta)
            negLL = -np.sum(norm.logpdf(ydata, loc=yPred, scale=1))
            return negLL

        initParams = [1, 1]
        results = minimize(gauss, initParams, method='Nelder-Mead')
        alpha_array.append(results.x[1])
        beta_array.append(results.x[0])
        success_array.append(results.success)
        estimated_param = results.x

        #  Goodness of Fit Procedure (R-Squared)
        Observe_y = ydata
        Expect_y = norm.cdf(xdata, loc=estimated_param[1], scale=estimated_param[0])
        correlation = np.corrcoef(Expect_y, Observe_y)
        r = correlation[0, 1]
        r_square = r**2
        r_square_array.append(r_square)

        #  plotting
        pathlib.Path(graph_path / str(parti_no)).mkdir(parents=True, exist_ok=True)
        filename = f"{graph_path}/{parti_no}/Condition{i + 1}.pdf"
        plt.clf()
        xforplot = np.arange(-30, 30.05, 0.05)
        yforplot = norm.cdf(xforplot, loc=estimated_param[1], scale=estimated_param[0])
        plt.plot(xdata, ydata, 'ko')
        plt.plot(xforplot, yforplot, 'k')
        plt.xlim(-35, 35)
        plt.ylim(-0.1, 1.1)
        plt.xlabel("Tilt (Degree in Clockwise)")
        plt.ylabel("Frequency of Responding Clockwise")
        plt.savefig(filename)
        plt.close()

    return fit_result


def output(result, data_path):
    out_data = np.array([])
    for i in range (len(result)):
        for j in range(len(result[i])):
            if j < 2:
                for k in range(len(result[i][j])):
                    out_data = np.append(out_data, result[i][j][k])

        if i < 1:
            out = pd.DataFrame([out_data])
            out.columns = ["Parti_No",
                            "Parti_Name",
                            "C1_Alpha",
                            "C2_Alpha",
                            "C3_Alpha",
                            "C1_Beta",
                            "C2_Beta",
                            "C3_Beta",
                            "C1_Success",
                            "C2_Success",
                            "C3_Success",
                            "C1_R_Square",
                            "C2_R_Square",
                            "C3_R_Square",]
        else:
            out.loc[i] = out_data
        out_data = []

    out.to_csv(f"{data_path}" + "/fit_result.csv", sep=',', index = False)

    return out


def analysis(data):
    # Transform dataset for statsmodels
    parti_no = []
    condition = []
    alpha = []
    beta = []
    r_square = []

    parti_no = data['Parti_No'].tolist()
    parti_no = parti_no * 3
    for i in range(len(data)):
        for j in range (3):
            condition.append(j+1)
    condition.sort()
    alpha = data['C1_Alpha'].tolist() + data['C2_Alpha'].tolist() + data['C3_Alpha'].tolist()
    beta = data['C1_Beta'].tolist() + data['C2_Beta'].tolist() + data['C3_Beta'].tolist()
    r_square = data['C1_R_Square'].tolist() + data['C2_R_Square'].tolist() + data['C3_R_Square'].tolist()
    alpha = [float(i) for i in alpha]
    beta = [float(i) for i in beta]
    r_square = [float(i) for i in r_square]

    transformed = pd.DataFrame({'parti_no':parti_no,
                                'condition':condition,
                                'alpha':alpha,
                                'beta':beta,
                                'r_square':r_square
                                })

    # Analysis Procedure
    # Sphercity test
    alpha_sph = pg.sphericity(transformed, dv = 'alpha', within = 'condition',
                              subject = 'parti_no',
                              method = 'mauchly', alpha = 0.05)
    beta_sph = pg.sphericity(transformed, dv = 'beta', within = 'condition',
                              subject = 'parti_no',
                              method = 'mauchly', alpha = 0.05)
    r_square_sph = pg.sphericity(transformed, dv = 'r_square', within = 'condition',
                              subject = 'parti_no',
                              method = 'mauchly', alpha = 0.05)

    # One way anova and post hoc
    alpha_anova = pg.rm_anova(transformed, dv = 'alpha', within = 'condition',
                              subject = 'parti_no', detailed = True,
                              effsize = 'np2')
    beta_anova = pg.rm_anova(transformed, dv = 'beta', within = 'condition',
                             subject = 'parti_no', detailed = True,
                             effsize = 'np2')
    r_square_anova = pg.rm_anova(transformed, dv = 'r_square', within = 'condition',
                                 subject = 'parti_no', detailed = True,
                                 effsize = 'np2')

    # Post_Hoc with Bonferroni corrections
    alpha_posthoc =  pg.pairwise_ttests(transformed, dv = 'alpha', within = 'condition',
                                        subject = 'parti_no', padjust = 'bonf',
                                        effsize = 'cohen')
    beta_posthoc =  pg.pairwise_ttests(transformed, dv = 'beta', within = 'condition',
                                        subject = 'parti_no', padjust = 'bonf',
                                        effsize = 'cohen')
    r_square_posthoc =  pg.pairwise_ttests(transformed, dv = 'r_square', within = 'condition',
                                          subject = 'parti_no', padjust = 'bonf',
                                          effsize = 'cohen')


    def des(var):
        return [var.name, var.astype(float).mean(), var.astype(float).std()]


    print("*******************************************************************")
    print("Descriptive Statistics")
    print("*******************************************************************")
    print("format: [name, mean, sd]")
    print(des(data["C1_Alpha"]))
    print(des(data["C2_Alpha"]))
    print(des(data["C3_Alpha"]))
    print(des(data["C1_Beta"]))
    print(des(data["C2_Beta"]))
    print(des(data["C3_Beta"]))
    print(des(data["C1_R_Square"]))
    print(des(data["C2_R_Square"]))
    print(des(data["C3_R_Square"]))

    print()
    print("*******************************************************************")
    print("Alpha Results")
    print("*******************************************************************")
    print("Sphericity")
    print(alpha_sph)
    print("ANOVA")
    print(alpha_anova)
    print("Post_Hoc Bonferroni")
    print(alpha_posthoc)
    print("*******************************************************************")

    print()
    print("*******************************************************************")
    print("Beta Results")
    print("*******************************************************************")
    print("Sphericity")
    print(beta_sph)
    print("ANOVA")
    print(beta_anova)
    print("Post_Hoc Bonferroni")
    print(beta_posthoc)
    print("*******************************************************************")
    print("*******************************************************************")

    print()
    print("*******************************************************************")
    print("R Square Results")
    print("*******************************************************************")
    print("Sphericity")
    print(r_square_sph)
    print("ANOVA")
    print(r_square_anova)
    print("Post_Hoc Bonferroni")
    print(r_square_posthoc)
    print("*******************************************************************")


def stat_graph(data):
    # Only plot beta here
    plt.clf()
    Mean_Total_Beta = [data["C1_Beta"].astype(float).mean(),
                       data["C2_Beta"].astype(float).mean(),
                       data["C3_Beta"].astype(float).mean(),
                       ]
    Std_Total_Beta = (data["C1_Beta"].astype(float).std(),
                      data["C2_Beta"].astype(float).std(),
                      data["C3_Beta"].astype(float).std()
                       )

    labels = ['Single Element', 'LowSD-Set', 'HighSD-Set']
    font = font_manager.FontProperties(family='Garamond',
                                       size='10')
    fig, host = plt.subplots(figsize=(4,4))
    x_pos = np.arange(len(labels))
    width = 0.05

    host.set_xlabel("Experimental Conditions", fontname="Garamond", fontsize=12, fontweight="bold")
    host.set_ylabel(r'Perceptual Sensitivity $\beta$', fontname="Garamond", fontsize=12, fontweight="bold")

    host.bar([0.0, 0.1, 0.2], Mean_Total_Beta, yerr=[(0,0,0),Std_Total_Beta], width=width, capsize=2, color='#888888')

    host.set_xticks([0.0,0.1,0.2])
    host.set_xticklabels(labels, fontname="Garamond", fontsize=10)

    plot_name = "C:/Users/Herrick Fung/Desktop/Course Materials/Sem 4.1/\
PSY402 Research Thesis II/part2_result/beta_over_con.png"
    plt.tight_layout()
    fig.savefig(plot_name, format='png', dpi=384, transparent=False)
    plt.clf()
    plt.close()


def curve_graph(data):
    # Create Total Array
    # i refers parti; j refers condition
    total = np.zeros(shape=(3,7))
    for i in range(len(data)):
        for j in range(3):
            if i == 0:
                total[j] = data[i][j]
            else:
                total[j] = np.sum([total[j], data[i][j]], axis = 0)

    # curve fit for total array
    xdata = np.arange(-30, 31, 10)
    alpha_array = []
    beta_array = []

    for j in range(3):
        ydata = total[j]
        ydata = ydata / (len(data) * 36)

        def gauss(params):
            beta = params[0]
            alpha = params[1]
            yPred = norm.cdf(xdata, loc=alpha, scale=beta)
            negLL = -np.sum(norm.logpdf(ydata, loc=yPred, scale=1))
            return negLL

        initParams = [1, 1]
        results = minimize(gauss, initParams, method='Nelder-Mead')
        alpha_array.append(results.x[1])
        beta_array.append(results.x[0])

    # plot curve graph
    plt.clf()
    matplotlib.rcParams['mathtext.fontset'] = 'cm'
    plt.style.use('seaborn-whitegrid')
    xdatapoint = np.arange(-30, 31, 10)
    xforplot = np.arange(-30, 30.05, 0.05)
    plt.figure(figsize = (6,9))
    labels = ['Single Element', 'LowSD-Set', 'HighSD-Set']

    for j in range(3):
        plt.subplot(3, 1, j+1)
        plt.subplot(3, 1, j+1).text(-22.5, 0.9, labels[j], ha='center',
                                    fontsize=14, fontname='Garamond',
                                    fontweight='bold', color='black',
                                    bbox=dict(facecolor='white', edgecolor='gray',
                                              boxstyle='round,pad=0.2', alpha = 1
                                              ))

        # grey plot (all parti plot)
        for k in range(len(data)):
            yforplot = norm.cdf(xforplot, loc=data[k][3][j], scale=data[k][4][j])
            ydatapoint = np.array(data[k][j])/36
            plt.plot(xforplot, yforplot, 'grey', linewidth = 1, alpha = 0.6)
            plt.plot(xdatapoint, ydatapoint, 'o', color = 'grey', alpha = 0.3)

        # total plot (highlighted)
        yforplot = norm.cdf(xforplot, loc=alpha_array[j], scale=beta_array[j])
        ydatapoint = total[j] / (len(data) * 36)
        plt.plot(xforplot, yforplot, color = '#4E67C8', linewidth = 2.5, alpha = 0.8)
        plt.plot(xdatapoint, ydatapoint, 'o', color = '#4E67C8', alpha = 0.8)

        plt.xlim(-35, 35)
        plt.ylim(-0.1, 1.1)

    # Axis text
    plt.gcf().text(0.025, 0.5, "Frequency of Responding Clockwise",
                   rotation='vertical', va='center', fontsize=16,
                   fontname="Garamond", fontweight="bold")
    plt.gcf().text(0.5, 0.05, "Tilt (Degree in Clockwise)",
                   ha='center', fontsize=16, fontname='Garamond',
                   fontweight='bold')

    # export
    plot_name = "C:/Users/Herrick Fung/Desktop/Course Materials/Sem 4.1/\
PSY402 Research Thesis II/part2_result/psychometric.png"
    plt.savefig(plot_name, format='png', dpi=384, transparent = False)
    plt.clf()
    plt.close()


def main():
    in_path, out_data_path, out_graph_path = manage_path()
    i = 0
    for path in in_path:
        master = [e for e in path.iterdir() if e.match('*.csv')]
        session = [e for e in path.iterdir() if e.match('*.txt')]
        merged_session = read_files(master, session)
        for_fit, parti_info = preprocess(merged_session)
        fit_result = fit(for_fit, parti_info[0], out_graph_path)
        combine = [parti_info] + [fit_result]
        fit_combine = for_fit + fit_result
        if i == 0:
            merged_all = [combine]
            merged_fit = [fit_combine]
        else:
            merged_all  = merged_all + [combine]
            merged_fit = merged_fit + [fit_combine]
        i = i + 1

    for_analysis = output(merged_all, out_data_path)
    stat_output_filename = "C:/Users/Herrick Fung/Desktop/Course Materials/Sem 4.1/\
PSY402 Research Thesis II/part2_result/behavioral_stats.txt"
    sys.stdout = open(stat_output_filename, 'w')
    analysis(for_analysis)
    sys.stdout.close()
    stat_graph(for_analysis)
    curve_graph(merged_fit)


if __name__ == "__main__":
    main()
