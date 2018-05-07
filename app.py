# import necessary libraries
import pandas as pd
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")

inspector = inspect(engine)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
table_samples_metadata = Base.classes.samples_metadata
table_otu = Base.classes.otu
table_samples = Base.classes.samples

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route('/names')
# List of sample names
def names():
    # results = session.query(table_samples_metadata.__table__.columns.keys())
    results = table_samples.__table__.columns.keys()
    namesofsamples = []
    header = 'otu'
    for result in results:
        if result.startswith(header):
            print('header')
        else:
            namesofsamples.append(result)
    return jsonify(namesofsamples)


@app.route('/otu')
# List of OTU descriptions
def otu():
    results = session.query(table_otu.lowest_taxonomic_unit_found).all()
    otu_descriptions = list(np.ravel(results))
    return jsonify(otu_descriptions)

@app.route('/metadata/<sample>')
# MetaData for a given sample.
#    Args: Sample in the format: `BB_940`
def metadata(sample):
    
    print(sample)
    sample = sample[3:]
    print(sample)

    query_meta_dict = {}
    results2 = session.query(table_samples_metadata).all()
    # print(results2[1].SAMPLEID)
    print(sample)
    for i in results2:
        # print(i.SAMPLEID)
        if i.SAMPLEID == int(sample):
            print('found')
            print('\n ')
            query_meta_dict = {
                "AGE": i.AGE,
                "BBYTPE": i.BBTYPE,
                "ETHNICITY": i.ETHNICITY,
                "GENDER": i.GENDER,
                "LOCATION": i.LOCATION,
                "SAMPLEID": i.SAMPLEID
                }   
            print(query_meta_dict)
    return jsonify(query_meta_dict)
    

@app.route('/wfreq/<sample>')
# Weekly Washing Frequency as a number.
#    Args: Sample in the format: `BB_940`
def wfreq(sample):
    print(sample)
    sample = sample[3:]
    print(sample)
    results2 = session.query(table_samples_metadata).all()
    # print(results2[1].SAMPLEID)
    print(sample)
    for i in results2:
        # print(i.SAMPLEID)
        if i.SAMPLEID == int(sample):
            print('found')
            print('\n ')
            print(i.WFREQ)
            i_frequency = int(i.WFREQ)
            print(i_frequency)
    return jsonify(i_frequency)

@app.route('/samples/<sample>')
# OTU IDs and Sample Values for a given sample.
def samples_func(sample):
    list_of_dicts = []
    print(sample)
    # sample = sample[3:]
    # print(sample)
    sel='samples.{}'.format(sample)
    results = session.query(table_samples.otu_id,sel).all()
    print(results)
    df_results = pd.DataFrame(results,columns=['OTU_ID','Sample_Values']).sort_values('Sample_Values',ascending=False)
   
    list_otu_id = list(df_results['OTU_ID'].astype('str'))
    list_sample_values = list(df_results['Sample_Values'].astype('str'))
    dict_otu_id = {
        'otu_ids': list_otu_id,
        'sample_values': list_sample_values
    }
    # list_of_dicts = {'otu_ids':list_otu_id,'sample_values':list_sample_values}
    list_of_dicts = [dict_otu_id]
    # print(list_of_dicts)
    return jsonify(list_of_dicts)


# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
