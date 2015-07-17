#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import os
import json
import csv

if len(sys.argv) != 2:
    print('usage: %s filename' % sys.argv[0])
    quit()

csvpath = sys.argv[1]

def make_jsonpath(category_name):
    jsonpath = os.path.abspath('%s.geojson' % category_name)
    if os.path.dirname(jsonpath) != os.getcwd():
        # ディレクトリトラバーサル対策 (念のため)
        raise RuntimeError('施設ジャンル名にパス区切り文字が含まれてゐるため中断しました: %s' % category_name)
    return jsonpath

with open(csvpath, 'r') as fp:
    reader = csv.reader(fp)

    # 必要なカラムの位置をヘッダーから調べる
    header = next(reader)
    col_name = header.index('ページタイトル')
    col_category = header.index('施設ジャンル')
    col_kana = header.index('施設、場所、イベントの名称（読み）')
    col_postcode = header.index('郵便番号')
    col_addr = header.index('住所')
    col_building_name = header.index('ビル名')
    col_floor = header.index('フロア数')
    col_lat = header.index('緯度')
    col_lon = header.index('経度')

    num_columns = len(header)

    # 直前に読んでゐたカテゴリを記憶する変数 (カテゴリ単位でファイルを分割するため)
    prev_category = None
    output_features = []

    for row in reader:
        if len(row) != num_columns:
            # ヘッダーと列数が一致しない行は無視する
            continue

        category = row[col_category]
        if category != prev_category and output_features != []:
            # カテゴリ単位で読み込んだデータを JSON としてに書き出す
            jsonpath = make_jsonpath(prev_category)
            with open(jsonpath, 'w') as jsonfp:
                geojson = {
                    'type': 'FeatureCollection',
                    'copyright': 'この GeoJSON ファイルは、以下の著作物を改変して利用しています。\n' \
                        '公共施設位置情報、千葉市、クリエイティブ・コモンズ・表示2.1 (http://creativecommons.org/licenses/by/2.1/jp/)',
                    'timestamp': '',
                    'crs': {
                        'type': 'name',
                        'properties': { 'name': 'urn:ogc:def:crs:OGC:1.3:CRS84' },
                    },
                    'features': output_features,
                }
                json.dump(geojson, jsonfp, indent = 4, sort_keys = True, ensure_ascii = False)
            output_features = []
        prev_category = category

        poi = {
            'type': 'Feature',
            'properties': {
                'name': row[col_name],
                'name_kana': row[col_kana],
                'category': row[col_category],
                'address': row[col_addr],
            },
            'geometry': {
                'type': 'Point',
                'coordinates': (float(row[col_lon]), float(row[col_lat])),
            },
        }

        if row[col_postcode] != '':
            poi['properties']['postcode'] = row[col_postcode]
        if row[col_building_name] != '':
            poi['properties']['building_name'] = row[col_building_name]
        if row[col_floor] != '':
            poi['properties']['floor'] = row[col_floor]

        output_features.append(poi)

# vim: et fenc=utf-8 sts=4 sw=4 ts=4
