'''
Input file: /result/raw/[Parti_Name]/behavioral/
Output file (Data): /result/curve_fitting/data/
Output file (Graph): /result/curve_fitting/graph/
#
The script will read the raw behavioral result from the raw directory,
return unmerged file for each participants on psychometric curve, in data directory,
also return graph for each conditions for each participants in graph directory.
'''

from scipy.optimize import minimize
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pathlib


def manage_path():
    #  in
    current_path = pathlib.Path(__file__).parent.absolute()
    raw_path = current_path / 'raw'
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
                out_data = np.append(out_data, result[i][j])
            else:
                for k in range(len(result[i][j])):
                    out_data = np.append(out_data, result[i][j][k])

    out_data = pd.DataFrame(out_data)
    out_data = out_data.transpose()
    out_data.columns = ["Parti_No",
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
                        "C3_R_Square",
                        ]
    out_data.to_csv(f"{data_path}" + "/fit_result.csv", sep=',', index = False)

    return out_data


def analysis(data):
    pass


def stat_graph():
    pass


def curve_graph():
    pass


def main():
    in_path, out_data_path, out_graph_path = manage_path()
    for path in in_path:
        master = [e for e in path.iterdir() if e.match('*.csv')]
        session = [e for e in path.iterdir() if e.match('*.txt')]
        merged_session = read_files(master, session)
        for_fit, parti_info = preprocess(merged_session)
        fit_result = fit(for_fit, parti_info[0], out_graph_path)
        merged_parti = []
        merged_parti.append(parti_info + fit_result)
    for_analysis = output(merged_parti, out_data_path)
    analysis(for_analysis)
    stat_graph()
    curve_graph()

    print("done")


if __name__ == "__main__":
    main()
