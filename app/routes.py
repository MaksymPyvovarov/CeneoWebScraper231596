from app import app
from app.models.scraper import Scraper
from app.models.product import Product
from flask import render_template, request, redirect, url_for, send_file
import requests
import os
import json
import pandas as pd
import numpy as np
from io import BytesIO
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')

@app.route('/')
@app.route('/index')
def index():
  return render_template("index.html")

@app.route('/extract', methods=['GET', 'POST'])
def extract():
  if request.method == 'POST':
    product_id = request.form.get('product_id')
    scraper = Scraper(product_id)
    scraper.extract_opinions()
    if scraper.response_status_code != requests.codes['ok']:
      return render_template('extract.html', error = "Product does not exist")
    if scraper.opinions:
      product_name = scraper.product_name
      scraper.save_to_json()
      product = Product(product_id, product_name, scraper.opinions)
      product.create_charts()
      return redirect(url_for('product', product_id=product_id))
    return render_template('extract.html', error = "Product has no opinions")
  return render_template("extract.html")

@app.route('/products')
def products():
  if os.path.exists("app/opinions"):
    products = [filename.split(".")[0] for filename in os.listdir("app/opinions")]
  else:
    products = []
  products_list = []
  for product in products:
    jf = open(f"app/products/{product}.json", "r", encoding="UTF-8")
    single_product = json.load(jf)
    products_list.append(single_product)
  return render_template("products.html", products=products_list)


@app.route('/author')
def author():
  return render_template("author.html")

@app.route('/product/<product_id>')
def product(product_id):
  opinions = pd.read_json(f"app/opinions/{product_id}.json")
  return render_template("product.html", product_id=product_id, opinions=opinions.to_html(table_id="opinions"))

@app.route('/charts/<product_id>')
def charts(product_id):
  return render_template("charts.html", product_id=product_id)


@app.route('/download/json/<product_id>')
def download_json(product_id):
  return send_file(f"opinions/{product_id}.json", mimetype='text/json', download_name=f'{product_id}.json', as_attachment=True)

@app.route('/download/csv/<product_id>')
def download_csv(product_id):
  opinions = pd.read_json(f"app/opinions/{product_id}.json")
  response_stream = BytesIO(opinions.to_csv().encode())
  return send_file(response_stream, mimetype='text/csv', download_name=f'{product_id}.csv', as_attachment=True)

@app.route('/download/xlsx/<product_id>')
def download_xlsx(product_id):
  opinions = pd.read_json(f"app/opinions/{product_id}.json")
  buffer = BytesIO()
  with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
      opinions.to_excel(writer)
  buffer.seek(0)
  return send_file(buffer, mimetype='application/vnd.ms-excel', download_name=f'{product_id}.xlsx', as_attachment=True)