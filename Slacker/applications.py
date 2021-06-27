import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify

app = Flask(__name__)


@app.route('/')
def home():
  return render_template('layout.html')


@app.route('/login')
def login():
  return render_template('login.html')


@app.route('/chat')
def signup():
  return render_template('sample.html')


if __name__ == "__main__":
  app.run(debug=True)
