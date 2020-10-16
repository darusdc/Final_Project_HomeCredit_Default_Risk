from flask import Flask, render_template, url_for, jsonify,abort,make_response,redirect,request
import pandas as pd
import numpy as np
import json
import plotly
import plotly.graph_objs as go
import random
import joblib
import sqlalchemy as db
import mysql.connector
## Pisahkan PCB, CBC, dan PA
app=Flask(__name__)
con=mysql.connector.connect(
    host='localhost',
    user='Darus',
    passwd='admin')
cur=con.cursor()
cur.execute('show databases')
dbms=cur.fetchall()
datava=False
for i in dbms:
    if i[0]=='flask_data':
        datava=True
        break
if datava== False:
    cur.execute('create database flask_data')
    engine1=db.create_engine('mysql+pymysql://Darus:admin@localhost:3306/flask_data')
    con2=engine1.connect()
    data=pd.read_csv('bersih.csv')
    data.drop(['Unnamed: 0','FLAG_DOCUMENT_2'],axis=1,inplace=True)
    data.to_sql('data',con=con2,index=True)
    datava=True
else:
    engine1=db.create_engine('mysql+pymysql://Darus:admin@localhost:3306/flask_data')
    con2=engine1.connect()
data=pd.read_sql('select * from data',con2)
data.drop('index',axis=1,inplace=True)
# data.drop(index=data[data['CODE_GENDER']=='XNA'].index,inplace=True)
list_plot=[('histplot','Histogram'),('boxplot','Box')]
x_list=[(x,x.replace('_'," ")) for x in data.columns if data[x].dtype=='object']
y_list=[(x,x.replace('_'," ")) for x in data.columns if data[x].dtype!='object']
hue_list=[(x,x.replace('_'," ")) for x in data.columns if (data[x].dtype=='object')&(data[x].nunique()<=5)]
list_estimator=[('count','Count'),('avg','Average'),('max','Max'),('min','Min')]
data_list=[list(data[i]) for i in data.columns]
data_zip=dict(zip(list(data.columns),data_list))
def category_plot(dfTips=data,cat_plot='histplot', cat_x=x_list[0][0], cat_y=y_list[0][0], estimator='count', hue=hue_list[0][0]):

    if cat_plot == 'histplot':

        data = []

        for val in dfTips[hue].unique(): #['Yes', 'No']
            hist = go.Histogram(
                x=dfTips[dfTips[hue] == val][cat_x],
                y=dfTips[dfTips[hue] == val][cat_y],
                histfunc= estimator,
                name = val
            )

            data.append(hist)

            title = 'Histogram'
        
    
    elif cat_plot == 'boxplot':
        data = []

        for val in dfTips[hue].unique(): #['Yes', 'No']
            box = go.Box(
                x=dfTips[dfTips[hue] == val][cat_x],
                y=dfTips[dfTips[hue] == val][cat_y],
                name = val
            )

            data.append(box)

            title = 'Box'     
    
    layout = go.Layout(
        title=title,
        xaxis=dict(title=cat_x),
        yaxis=dict(title=cat_y),
        boxmode='group'
    )


    res = {"data": data, 'layout': layout}
    graphJSON = json.dumps(res, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
def pie(dfTips=data,hue=hue_list[0][0]):
    vcounts=dfTips[hue].value_counts()
    labels=[]
    values=[]
    for item in vcounts.iteritems():
        labels.append(item[0])
        values.append(item[1])
    data= [go.Pie(labels=labels,values=values)]
    layout=go.Layout(title='Pie')
    res={'data': data, 'layout':layout}

    graphJSON = json.dumps(res, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
def color():
    return ("#"+str("".join([random.choice('0123456789ABCDEF') for x in range(6)])))
def scatter_plot(dfTips=data.iloc[range(0,1000)],cat_x=x_list[0][0],cat_y=y_list[0][0],hue=hue_list[0][0]):
    data=[]
    for val in dfTips[hue].unique():
        scat=go.Scatter(x=dfTips[dfTips[hue]==val][cat_x],
        y=dfTips[dfTips[hue]==val][cat_y], mode='markers',
        name=val
        )
        data.append(scat)
    layout=go.Layout(title='Scatter',title_x=0.5, 
    xaxis= dict(title=cat_x), yaxis=dict(title=cat_y))
    res={'data': data, 'layout':layout}

    graphJSON = json.dumps(res, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
@app.route('/')
def home():
    data1=data.copy()
    return render_template(
        'home.html',
        active='Dashboard',
        data=data1[data1.columns],
        cat=x_list,
        color=[color() for x in range(len(data1.columns))],
        focus='CODE_GENDER'
        )
@app.route('/davis')
def davis():
    data1=data.copy()
    return render_template(
        'category.html',
        active='davis',
        drop_plot=list_plot,
        drop_x=x_list,
        drop_y=y_list,
        drop_estimator=list_estimator,
        drop_hue=hue_list,
        drop_hue_pie=hue_list,
        focus_plot=list_plot[0][0],
        focus_x=x_list[0][0],
        focus_y=y_list[0][0],
        focus_estimator=list_estimator[0][0],
        focus_hue=hue_list[0][0],
        focus_hue_pie=hue_list[0][0],
        plot=category_plot(dfTips=data1),
        pie=pie(),
        scat=scatter_plot()
        )
@app.route('/davis/cat_fn/<nav>')
def cat_fn(nav):
    if nav=='True':
        cat_plot="histplot"
        cat_x=x_list[0][0]
        cat_y=y_list[0][0]
        estimator="count"
        hue=hue_list[0][0]
        hue_pie=hue
        cat_x_scat=cat_x
        cat_y_scat=cat_y
        hue_scat=hue
    else:
        cat_plot=request.args.get('cat_plot')
        cat_x=request.args.get('cat_x')
        cat_y=request.args.get('cat_y')
        estimator=request.args.get('estimator')
        hue=request.args.get('hue')
        hue_pie=request.args.get('hue_pie')
        cat_x_scat=request.args.get('cat_x_scat')
        cat_y_scat=request.args.get('cat_y_scat')
        hue_scat=request.args.get('hue_scat')
    if estimator==None:
        estimator='count'
    if cat_y==None:
        cat_y=y_list[0][0]
    if hue_pie==None:hue_pie=hue_list[0][0]
    if cat_plot==None:cat_plot="histplot"
    if cat_x==None:cat_x=x_list[0][0]
    if hue==None:hue=hue_list[0][0]
    if cat_x_scat==None:cat_x_scat=cat_x
    if cat_y_scat==None:cat_y_scat=cat_y
    if hue_scat==None:hue_scat=hue
    # data1=data.drop(index=data[data['CODE_GENDER']=='XNA'].index)
    plot=category_plot(cat_plot=cat_plot,cat_x=cat_x,cat_y=cat_y,estimator=estimator,hue=hue)
    pie_plot=pie(hue=hue_pie)
    scat=scatter_plot(cat_x=cat_x_scat,cat_y=cat_y_scat,hue=hue_scat)
    return render_template(
        'category.html',
        active='davis',
        drop_plot=list_plot,
        drop_x=x_list,
        drop_y=y_list,
        drop_estimator=list_estimator,
        drop_hue=hue_list,
        drop_hue_pie=hue_list,
        focus_plot=cat_plot,
        focus_x=cat_x,
        focus_x_scat=cat_x_scat,
        focus_y=cat_y,
        focus_y_scat=cat_y_scat,
        focus_estimator=estimator,
        focus_hue=hue,
        focus_hue_pie=hue_pie,
        focus_hue_scat=hue_scat,
        plot=plot,
        pie=pie_plot,
        scat=scat
        )
@app.route('/tentang')
def tentang():
    return render_template(
        'tentang.html',active='about'
    )
@app.route('/predict')
def predict():
    data1=data.copy()
    data1=data1.drop(['TARGET'],axis=1)
    return render_template(
        'predict.html',
        active='ML',
        data=data1
    )
@app.route('/result',methods=['POST'])
def result():
    data1=data.copy()
    data1=data1.drop(['TARGET'],axis=1)
    data1['CILUT']=data['AMT_ANNUITY']/data['AMT_CREDIT']*100
    data1['CILMAS']=data['AMT_ANNUITY']/data['AMT_INCOME_TOTAL']*100
    data1['RUTHAR']=data['AMT_GOODS_PRICE']/data['AMT_CREDIT']*100
    features=list(pd.get_dummies(data1).columns)
    data_input=[0 for i in range(0,len(features))]
    data_comp=dict(zip(features,data_input))
    if request.method=='POST':
        user=request.form
        input_user=[user[i]if i!='AGE' or i!='EMPLOYED_YEARS' else user[i]*(-365) for i in user]
        for i in range(0,len(data1.columns)-3):
            print(data1.columns[i])
            if data1[data1.columns[i]].dtype=='object':
                data_comp[data1.columns[i]+'_'+input_user[i]]=1
            else:
                data_comp[data1.columns[i]]=float(input_user[i])
        data_comp['CILUT']=data_comp['AMT_ANNUITY']/data_comp['AMT_CREDIT']*100
        data_comp['CILMAS']=data_comp['AMT_ANNUITY']/data_comp['AMT_INCOME_TOTAL']*100
        data_comp['RUTHAR']=data_comp['AMT_GOODS_PRICE']/data_comp['AMT_CREDIT']*100
        # predict=ml.predict([list(data_comp.values())])
        predict_prob=ml.predict_proba([list(data_comp.values())])
        predict=[0 if x[1]<0.500084 else 1 for x in predict_prob]
    return render_template('result.html',active='ML',predict=predict,predict_proba=predict_prob)

@app.route('/insert')
def input():
    data1=pd.DataFrame()
    data1['No']=[x for x in range(1,len(data)+1)]
    for i in data.columns:
        if i!='index': data1[i]=data[i]
    data_html=[]
    for i in range(-100,0):
        data_temp=[]
        for x in data1.columns:
            data_temp.append(data1[x][len(data1)+i])
        data_html.append(data_temp)
    return render_template('insert.html',active='ND',data=data1, data_table=data_html)
@app.route('/push',methods=['POST'])
def progress():
    global data
    columns=list(data.columns)
    data_input=[0 for x in range(len(data.columns))]
    data_comp=dict(zip(columns,data_input))
    if request.method=='POST':
        user=request.form
        input_user=[user[i] for i in user]
        for i in range(0,len(columns)):
            # print(data.columns[i],data.columns[i].dtype)
            if data.columns[i]=='index':
                data_comp[data.columns[i]]=len(data)
            else:
                    
                if data[data.columns[i]].dtype=='object':
                    data_comp[data.columns[i]]=input_user[i-1]
                else:
                    if input_user[i-1].find('.')==-1:
                        data_comp[data.columns[i]]=int(input_user[i-1],32)
                    else:
                        data_comp[data.columns[i]]=float(input_user[i-1])
    data=data.append(data_comp,ignore_index=True)
    data.iloc[[-1]].to_sql('data',con2,if_exists='append',index=True)
    return render_template('sukses.html')
if __name__== "__main__":
    # ml=joblib.load('model_rfc_ros')
    ml=joblib.load('ada_model')
    app.run(debug=True,port=4000)
