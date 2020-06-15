from flask import Flask, render_template, request
from string import Template
import pandas as pd
from sklearn.linear_model import LinearRegression

#New step added
#Creating a dummy dataframe similar to ENV_DATA (removed ENV_REF column)
dummy_ENV_DATA = pd.DataFrame({'date'   : ['06-May-2020','07-May-2020','08-May-2020','08-May-2020','09-May-2020',
                                           '10-May-2020','11-May-2020','12-May-2020','13-May-2020','14-May-2020'],
                               'Proc_Id': ['8000','8500','9000','9500','10000','10500','11000','11500',
                                          '12000','12500'],
                               'Activity':[10000,20078,93000,5555,3234,6565,1212,2564,5656,5677],
                               'Transaction':[200,2,300,5445,3434,2123,5432,1234,1111,1233]})

 #Creating a dummy dataframe similar to CTLM_JOB(removed ENV_REF column)
dummy_ControlM_DATA =pd.DataFrame({'date': ['06-May-2020','07-May-2020','08-May-2020','08-May-2020','09-May-2020',
                                            '10-May-2020','11-May-2020','12-May-2020','13-May-2020','14-May-2020'],
                                   'Proc_Id':['8000','8500','9000','9500','10000','10500','11000','11500',
                                              '12000','12500'],
                                   'RUN_TIME_ELAPSED_IN_SECONDS': [15,67,30,34,78,19,23,87,21,47]})

 #%Using Merge function
df_final_aftrmerge = pd.merge(dummy_ENV_DATA,dummy_ControlM_DATA, how='left',
                     left_on=['date', 'Proc_Id'],
                     right_on=['date', 'Proc_Id'])

app = Flask(__name__,template_folder="C:\sei_python")
@app.route('/')
def sei_frontend():
   return render_template('sei_frontendvalues.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      ## new code added here
      column_names = ['Proc_Id', 'date', 'Activity']                
      df_2 = pd.DataFrame(columns = column_names)
      proc_id = request.form.get('procid')
      date = request.form.get('date')
      activity = request.form.get('Activity')
      temp_list = []
      temp_list.extend([proc_id, date, activity])
      df_2 = df_2.append(pd.Series(temp_list, index=df_2.columns), ignore_index=True)
      #print(df_2)
      global corr_tb
      corr_tb = df_2
      corr_tb['RUN_TIME_ELAPSED_IN_SECONDS'] = 0
      print(corr_tb)
      global df_3
      df_3=pd.concat([corr_tb,df_final_aftrmerge], axis=0, ignore_index=True)
      #Removing NaN from Transition column
      df_3["Transaction"] = df_3["Transaction"].fillna(0)
      print(df_3)

      #LinearRegression Code
      global X_t, Y_t
      X_t = df_3.drop(["date","Proc_Id","RUN_TIME_ELAPSED_IN_SECONDS"],1)
      Y_t = df_3['RUN_TIME_ELAPSED_IN_SECONDS']

      #Model Instance creation
      lin_reg_mod = LinearRegression()

      #Model Fit
      lin_reg_mod.fit(X_t,Y_t)

      #Prediction from Model
      global pred_t
      pred_t = lin_reg_mod.predict(X_t)
      print(pred_t)

      #Concatenate predicted value with input given dataset
      global Predicted_Output, Export_Predicted_Output
      Predicted_Output = pd.concat([X_t, pd.DataFrame(pred_t)], axis=1)
      Predicted_Output.rename(columns={0:'Predicted RunTime'}, inplace=True )
      print(Predicted_Output.head(1))
      Export_Predicted_Output=Predicted_Output.head(1)

      shutdown_server()
      # return('',204)
      return Export_Predicted_Output.to_html(header="true", table_id="table")

#Shutting down web-Services function
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

#     return ('',204)
if __name__ == '__main__':
    app.run()
