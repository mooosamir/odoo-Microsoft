# -*- coding: utf-8 -*-

import gevent.monkey
# gevent.monkey.patch_all()
# from gevent import monkey as curious_george
# curious_george.patch_all(thread=False, select=False)
# import grequests
import json
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import requests
from odoo import models, fields, api, exceptions


class FramesData(models.Model):
    _name = 'frames.data'
    _description = 'frames.data'

    name = fields.Char()

    def get_vendors(self):
        data = []
        vendor_ids = self.env['res.partner'].search([('supplier_rank', '>=', 1)])
        vendor_ids.filtered(lambda x: 'Frame' in x.category_id.mapped('name'))
        for vendor in vendor_ids:
            data.append({
                'id': vendor.id,
                'name': vendor.name,
            })
        return data

    def get_frames_data_config(self):
        base_url = 'http://api.framesdata.com:80/'
        partner_id = 'CA6B165B-C4C8-4D0D-9C1A-1ECA9B01F387'
        username = self.env['ir.config_parameter'].sudo().search([('key', '=', 'fd_username')]).value
        szipcode = self.env['ir.config_parameter'].sudo().search([('key', '=', 'fd_szipcode')]).value
        bzipcode = self.env['ir.config_parameter'].sudo().search([('key', '=', 'fd_bzipcode')]).value
        locations = self.env['ir.config_parameter'].sudo().search([('key', '=', 'fd_locations')]).value

        return base_url, partner_id, username, szipcode, bzipcode, locations \
            if base_url and partner_id and username and szipcode and bzipcode and locations else None

    def get_token(self):
        general_settings = self.get_frames_data_config()
        link = str(general_settings[0])+"api/authenticatepms?partnerid=" + str(general_settings[1]) + "&username=" + str(general_settings[2]) + "&szipcode=" + str(general_settings[3]) + "&bzipcode=" + str(general_settings[4]) + "&locations=" + str(general_settings[5])
        try:
            response = requests.get(link)
            token = ''
            if response.status_code == 200:
                token = json.loads(response.text)['auth']['AuthorizationTicket']
            return general_settings[0], token
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_retail_by_wholesale(self, wholesale, cfmid):
        wholesale = float(wholesale)
        frame_markup_formula = self.env['frame.markup.formula'].search([])
        found = False
        for records in frame_markup_formula:
            for data in records.collection_id:
                if str(data.cfmid) == str(cfmid):
                        found = True
                        break
            if found:
                break

        if not found:
            collection_id = frame_markup_formula.filtered(lambda x: x.collection_id.ids == [])
            if len(collection_id) > 1:
                collection_id = collection_id[0]
            if collection_id.id:
                records = collection_id
            else:
                return 0

        if records.w_price_min < wholesale < records.w_price_max:
            wholesale = wholesale * records.multiplier
            wholesale = wholesale + records.additional_amt
            wholesale = int(wholesale) + records.ends_with
            if records.next_ten:
                wholesale = round(wholesale + 5.1, -1)
            return wholesale
        else:
            return 0

    def get_manufacturers_and_collections(self, discontinued_=None):
        general_settings = self.get_token()
        manufacturers_link = str(general_settings[0]) + "api/manufacturers?auth=" + str(general_settings[1])
        collections_link = str(general_settings[0]) + "api/collections?auth=" + str(general_settings[1])
        collections_data = {}
        manufacturers_data = []
        try:
            response = requests.get(collections_link)
            discontinued_collections = 0
            if response.status_code == 200:
                response_data = json.loads(response.text)['Collections']
                for collection in response_data:
                    if collection['Status'] == 'D':
                        discontinued_collections += 1
                    elif collection['ManufacturerFramesMasterID'] in collections_data:
                        collections_data[collection['ManufacturerFramesMasterID']].append({
                            'ManufacturerFramesMasterID': collection['ManufacturerFramesMasterID'],
                            'BrandFramesMasterID': collection['BrandFramesMasterID'],
                            'CollectionFramesMasterID': collection['CollectionFramesMasterID'],
                            'CollectionName': collection['CollectionName'],
                            'Market': collection['Market'],
                            'Status': collection['Status'],
                        })
                    elif collection['ManufacturerFramesMasterID'] not in collections_data:
                        collections_data[collection['ManufacturerFramesMasterID']] = []
                        collections_data[collection['ManufacturerFramesMasterID']].append({
                            'ManufacturerFramesMasterID': collection['ManufacturerFramesMasterID'],
                            'BrandFramesMasterID': collection['BrandFramesMasterID'],
                            'CollectionFramesMasterID': collection['CollectionFramesMasterID'],
                            'CollectionName': collection['CollectionName'],
                            'Market': collection['Market'],
                            'Status': collection['Status'],
                        })

            response = requests.get(manufacturers_link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['Manufacturers']
                for manufacturer in response_data:
                    if manufacturer['ManufacturerFramesMasterID'] in collections_data:
                        for collection in collections_data[manufacturer['ManufacturerFramesMasterID']]:
                            collection['name'] = manufacturer['ManufacturerName'] + " / " + collection['CollectionName']
                            collection['ManufacturerName'] = manufacturer['ManufacturerName']
                            collection['CollectionName'] = collection['CollectionName']
                            manufacturers_data.append(collection)
                return manufacturers_data
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_styles_by_model_name(self, model_name):
        general_settings = self.get_token()
        manufacturers_link = str(general_settings[0]) + "api/manufacturers?auth=" + str(general_settings[1])

        data = []
        styles_link = []
        try:
            response = requests.get(manufacturers_link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['Manufacturers']
                for manufacturer in response_data:
                    styles_link.append(str(general_settings[0]) + "api/manufacturers/" + str(manufacturer['ManufacturerFramesMasterID']) + "/styles?auth=" + str(
                        general_settings[1]))
            with FuturesSession() as session:
                futures = [session.get(u) for u in styles_link]
                for future in as_completed(futures):
                    styles_response = future.result()
                    # print(resp.json()['url'])
            # rs = (grequests.get(u) for u in styles_link)
            # response = grequests.map(rs)
            # for styles_response in response:
                    if styles_response.status_code == 200:
                        styles_response_data = json.loads(styles_response.text)['Styles']
                        for style in styles_response_data:
                            if model_name.upper() in style['StyleName'].upper():
                                data.append({
                                    'ManufacturerFramesMasterID': style['ManufacturerFramesMasterID'],
                                    'BrandFramesMasterID': style['BrandFramesMasterID'],
                                    'CollectionFramesMasterID': style['CollectionFramesMasterID'],
                                    'StyleFramesMasterID': style['StyleFramesMasterID'],

                                    'ManufacturerName': style['ManufacturerName'],
                                    'BrandName': style['BrandName'],
                                    'CollectionName': style['CollectionName'],
                                    'StyleName': style['StyleName'],
                                    # required for save
                                    'StyleStatus': style['StyleStatus'],
                                    'StyleDiscontinuedOn': style['StyleDiscontinuedOn'],
                                    'Material': style['Material'],
                                    'Shape': style['FrameShape'],
                                    'Age': style['Age'],
                                    'GenderType': style['Gender'],
                                    'FrameType': style['FrameType'],
                                    'Rim': style['Rim'],
                                    'EdgeType': style['EdgeType'],
                                    'Bridge': style['BridgeDescription'],
                                    'Hinge': style['Hinge'],
                                    'LensType': style['LensDescription'],
                                    'RX': style['RX'],
                                    'ClipOnOption': style['ClipSunglass'],
                                    'Sideshields': style['Sideshields'],
                                    'Warranty': style['Warranty'],
                                    'Sunglasses': style['ProductGroup'],
                                })
                                data[-1]['json'] = json.dumps(data[-1])
                        styles_response.close()
            return data
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_manufacturers(self):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "api/manufacturers?auth=" + str(general_settings[1])
        try:
            response = requests.get(link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['Manufacturers']
                data = []
                for manufacturer in response_data:
                    data.append({
                        'ManufacturerFramesMasterID': manufacturer['ManufacturerFramesMasterID'],
                        'ManufacturerName': manufacturer['ManufacturerName'],
                        'Market': manufacturer['Market'],
                        'Status': manufacturer['Status'],
                    })
                return data
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_collections(self):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "api/collections?auth=" + str(general_settings[1])
        try:
            response = requests.get(link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['Collections']
                data = []
                for collection in response_data:
                    data.append({
                        'ManufacturerFramesMasterID': collection['ManufacturerFramesMasterID'],
                        'BrandFramesMasterID': collection['BrandFramesMasterID'],
                        'CollectionFramesMasterID': collection['CollectionFramesMasterID'],
                        'CollectionName': collection['CollectionName'],
                        'Market': collection['Market'],
                        'Status': collection['Status'],
                    })
                return data
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_collections_by_mfmid(self, mfmid):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "api/manufacturers/" + str(mfmid) + "/collections?auth=" + str(general_settings[1])
        try:
            response = requests.get(link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['Collections']
                data = []
                for collection in response_data:
                    data.append({
                        'ManufacturerFramesMasterID': collection['ManufacturerFramesMasterID'],
                        'BrandFramesMasterID': collection['BrandFramesMasterID'],
                        'CollectionFramesMasterID': collection['CollectionFramesMasterID'],
                        'CollectionName': collection['CollectionName'],
                        'Market': collection['Market'],
                        'Status': collection['Status'],
                    })
                return data
            else:
                return []
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_collections_and_styles_by_mfmid(self, mfmid):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "api/manufacturers/" + str(mfmid) + "/styles?auth=" + str(general_settings[1])
        try:
            response = requests.get(link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['Styles']
                data = []
                for style in response_data:
                    data.append({
                        'ManufacturerFramesMasterID': style['ManufacturerFramesMasterID'],
                        'BrandFramesMasterID': style['BrandFramesMasterID'],
                        'CollectionFramesMasterID': style['CollectionFramesMasterID'],
                        'StyleFramesMasterID': style['StyleFramesMasterID'],

                        'ManufacturerName': style['ManufacturerName'],
                        'BrandName': style['BrandName'],
                        'CollectionName': style['CollectionName'],
                        'StyleName': style['StyleName'],
                    })
                return data, self.get_collections_by_mfmid(mfmid), self.get_styles_by_mfmid(mfmid)
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_styles_by_cfmid(self, cfmids):
        general_settings = self.get_token()
        data = []
        for cfmid in cfmids:
            link = str(general_settings[0]) + "api/collections/" + str(cfmid) + "/styles?auth=" + str(general_settings[1])
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    response_data = json.loads(response.text)['Styles']
                    for style in response_data:
                        data.append({
                            'ManufacturerFramesMasterID': style['ManufacturerFramesMasterID'],
                            'BrandFramesMasterID': style['BrandFramesMasterID'],
                            'CollectionFramesMasterID': style['CollectionFramesMasterID'],
                            'StyleFramesMasterID': style['StyleFramesMasterID'],

                            'ManufacturerName': style['ManufacturerName'],
                            'BrandName': style['BrandName'],
                            'CollectionName': style['CollectionName'],
                            'StyleName': style['StyleName'],
                            # required for save
                            'StyleStatus': style['StyleStatus'],
                            'StyleDiscontinuedOn': style['StyleDiscontinuedOn'],
                            'Material': style['Material'],
                            'Shape': style['FrameShape'],
                            'Age': style['Age'],
                            'GenderType': style['Gender'],
                            'FrameType': style['FrameType'],
                            'Rim': style['Rim'],
                            'EdgeType': style['EdgeType'],
                            'Bridge': style['BridgeDescription'],
                            'Hinge': style['Hinge'],
                            'LensType': style['LensDescription'],
                            'RX': style['RX'],
                            'ClipOnOption': style['ClipSunglass'],
                            'Sideshields': style['Sideshields'],
                            'Warranty': style['Warranty'],
                            'Sunglasses': style['ProductGroup'],
                        })
                        data[-1]['json'] = json.dumps(data[-1])
            except:
                raise exceptions.AccessDenied("Server error\n Please try again in few minutes")
        return data

    def get_styles_and_configurations_by_cfmid(self, cfmids, vendor):
        general_settings = self.get_token()
        data = []
        for cfmid in cfmids:
            link = str(general_settings[0]) + "api/collections/" + str(cfmid) + "/styles?auth=" + str(general_settings[1])
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    response_data = json.loads(response.text)['Styles']
                    for style in response_data:
                        data.append({
                            'ManufacturerFramesMasterID': style['ManufacturerFramesMasterID'],
                            'BrandFramesMasterID': style['BrandFramesMasterID'],
                            'CollectionFramesMasterID': style['CollectionFramesMasterID'],
                            'StyleFramesMasterID': style['StyleFramesMasterID'],

                            'ManufacturerName': style['ManufacturerName'],
                            'BrandName': style['BrandName'],
                            'CollectionName': style['CollectionName'],
                            'StyleName': style['StyleName'],
                            # required for save
                            'StyleStatus': style['StyleStatus'],
                            'StyleDiscontinuedOn': style['StyleDiscontinuedOn'],
                            'Material': style['Material'],
                            'Shape': style['FrameShape'],
                            'Age': style['Age'],
                            'GenderType': style['Gender'],
                            'FrameType': style['FrameType'],
                            'Rim': style['Rim'],
                            'EdgeType': style['EdgeType'],
                            'Bridge': style['BridgeDescription'],
                            'Hinge': style['Hinge'],
                            'LensType': style['LensDescription'],
                            'RX': style['RX'],
                            'ClipOnOption': style['ClipSunglass'],
                            'Sideshields': style['Sideshields'],
                            'Warranty': style['Warranty'],
                            'Sunglasses': style['ProductGroup'],
                        })
                        if len(data) > 0:
                            get_configurations_by_sfmid = self.get_configurations_by_sfmid(data[-1]['StyleFramesMasterID'])[0]
                            if len(get_configurations_by_sfmid) > 0:
                                retail = 0
                                wholesale = float(get_configurations_by_sfmid[0]['SalePrice'])

                                for record in get_configurations_by_sfmid:
                                    record['Wholesale'] = record['SalePrice']
                                    record['Retail'] = self.get_retail_by_wholesale(record['Wholesale'], data[-1]['CollectionFramesMasterID'])
                                    record['Min_Qty'] = 0
                                    record['Max_Qty'] = 0

                                    if float(record['Wholesale']) <= wholesale:
                                        wholesale = float(record['Wholesale'])
                                        retail = float(record['Retail'])

                                data[-1]['configurations'] = []
                                data[-1]['configurations'] = get_configurations_by_sfmid
                                data[-1]['Wholesale'] = wholesale
                                data[-1]['Retail'] = retail
                                data[-1]['Vendor'] = vendor
                            else:
                                data[-1]['configurations'] = []
                                data[-1]['Wholesale'] = 0
                                data[-1]['Retail'] = self.get_retail_by_wholesale(0, data[-1]['CollectionFramesMasterID'])
                                data[-1]['Vendor'] = vendor

            except Exception as e:
                print(e)
                # raise exceptions.AccessDenied(e)
                raise exceptions.AccessDenied("Server error\n Please try again in few minutes")
        return data

    def get_styles_by_mfmid(self, mfmid):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "api/manufacturers/" + str(mfmid) + "/styles?auth=" + str(general_settings[1])
        try:
            response = requests.get(link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['Styles']
                data = []
                for style in response_data:
                    data.append({
                        'ManufacturerFramesMasterID': style['ManufacturerFramesMasterID'],
                        'BrandFramesMasterID': style['BrandFramesMasterID'],
                        'CollectionFramesMasterID': style['CollectionFramesMasterID'],
                        'StyleFramesMasterID': style['StyleFramesMasterID'],

                        'ManufacturerName': style['ManufacturerName'],
                        'BrandName': style['BrandName'],
                        'CollectionName': style['CollectionName'],
                        'StyleName': style['StyleName'],
                        # required for save
                        'StyleStatus': style['StyleStatus'],
                        'StyleDiscontinuedOn': style['StyleDiscontinuedOn'],
                        'Material': style['Material'],
                        'Shape': style['FrameShape'],
                        'Age': style['Age'],
                        'GenderType': style['Gender'],
                        'FrameType': style['FrameType'],
                        'Rim': style['Rim'],
                        'EdgeType': style['EdgeType'],
                        'Bridge': style['BridgeDescription'],
                        'Hinge': style['Hinge'],
                        'LensType': style['LensDescription'],
                        'RX': style['RX'],
                        'ClipOnOption': style['ClipSunglass'],
                        'Sideshields': style['Sideshields'],
                        'Warranty': style['Warranty'],
                        'Sunglasses': style['ProductGroup'],
                    })
                    data[-1]['json'] = json.dumps(data[-1])
                return data
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_styles_by_sfmid(self, sfmid):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "api/styles/" + str(sfmid) + "?auth=" + str(general_settings[1])
        try:
            response = requests.get(link)
            if response.status_code == 200:
                style = json.loads(response.text)['Styles']
                data = []
                data.append({
                    'ManufacturerFramesMasterID': style['ManufacturerFramesMasterID'],
                    'BrandFramesMasterID': style['BrandFramesMasterID'],
                    'CollectionFramesMasterID': style['CollectionFramesMasterID'],
                    'StyleFramesMasterID': style['StyleFramesMasterID'],

                    'ManufacturerName': style['ManufacturerName'],
                    'BrandName': style['BrandName'],
                    'CollectionName': style['CollectionName'],
                    'StyleName': style['StyleName'],
                    # required for save
                    'StyleStatus': style['StyleStatus'],
                    'StyleDiscontinuedOn': style['StyleDiscontinuedOn'],
                    'Material': style['Material'],
                    'Shape': style['FrameShape'],
                    'Age': style['Age'],
                    'GenderType': style['Gender'],
                    'FrameType': style['FrameType'],
                    'Rim': style['Rim'],
                    'EdgeType': style['EdgeType'],
                    'Bridge': style['BridgeDescription'],
                    'Hinge': style['Hinge'],
                    'LensType': style['LensDescription'],
                    'RX': style['RX'],
                    'ClipOnOption': style['ClipSunglass'],
                    'Sideshields': style['Sideshields'],
                    'Warranty': style['Warranty'],
                    'Sunglasses': style['ProductGroup'],
                })
                data[-1]['json'] = json.dumps(data[-1])
                return data
            else:
                return []
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_configurations_by_sfmid(self, sfmid, i=-1):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "/api/styleconfigurations/" + str(sfmid) + "?auth=" + str(general_settings[1])
        try:
            response = requests.get(link)
            if response.status_code == 200:
                response_data = json.loads(response.text)['StyleConfigurations']
                data = []
                style = response_data
                for configuration in style['Configurations']:
                    data.append({
                        'ConfigurationFramesMasterID': configuration['ConfigurationFramesMasterID'],
                        'StyleFramesMasterID': configuration['StyleFramesMasterID'],

                        'SKU': configuration['SKU'],

                        'Eye': configuration['EyeSize'],
                        'Bridge': configuration['BridgeSize'],
                        'Temple': configuration['TempleLength'],
                        'Color': configuration['FrameColor'],
                        'ColorCode': configuration['FrameColorCode'],
                        'LensColor': configuration['LensColor'],
                        'Tags': '',
                        'Discontinued': configuration['ConfigurationStatus'],
                        'DiscontinuedDate': configuration['ConfigurationStatus'],
                        'A': configuration['A'],
                        'B': configuration['B'],
                        'DBL': configuration['DBL'],
                        'ED': configuration['ED'],
                        'EDAngle': configuration['EDAngle'],
                        'UPC': configuration['UPC'],

                        'ChangedPrice': configuration['ChangedPrice'],
                        'NewPrice': configuration['NewPrice'],
                        'ConfigurationStatus': configuration['ConfigurationStatus'],
                        'SalePrice': configuration['CompletePrice'],
                    })
                    if len(data) > 0:
                        data[-1]['Retail'] = self.get_retail_by_wholesale(configuration['CompletePrice'], style['CollectionFramesMasterID'])
                    # data[-1]['json'] = json.dumps(data[-1])
                return data, i
            else:
                return [],[]
        except Exception as e:
            # raise exceptions.AccessDenied(e)
            print(e)
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def get_configurations_by_upc(self, upc):
        general_settings = self.get_token()
        link = str(general_settings[0]) + "api/styleconfigurations?auth=" + str(general_settings[1]) + "&upc="  + str(upc)
        try:
            response = requests.get(link)
            if response.status_code == 200:
                styleconfiguration = json.loads(response.text)['StyleConfigurations']
                data = []
                if styleconfiguration['Configurations'] and len(styleconfiguration['Configurations']):
                    data.append({
                        'ManufacturerFramesMasterID': styleconfiguration['ManufacturerFramesMasterID'],
                        'BrandFramesMasterID': styleconfiguration['BrandFramesMasterID'],
                        'CollectionFramesMasterID': styleconfiguration['CollectionFramesMasterID'],
                        'StyleFramesMasterID': styleconfiguration['StyleFramesMasterID'],

                        'ManufacturerName': styleconfiguration['ManufacturerName'],
                        'BrandName': styleconfiguration['BrandName'],
                        'CollectionName': styleconfiguration['CollectionName'],
                        'StyleName': styleconfiguration['StyleName'],
                        # required for save
                        'StyleStatus': styleconfiguration['StyleStatus'],
                        'StyleDiscontinuedOn': styleconfiguration['StyleDiscontinuedOn'],
                        'Material': styleconfiguration['Material'],
                        'Shape': styleconfiguration['FrameShape'],
                        'Age': styleconfiguration['Age'],
                        'GenderType': styleconfiguration['Gender'],
                        'FrameType': styleconfiguration['FrameType'],
                        'Rim': styleconfiguration['Rim'],
                        'EdgeType': styleconfiguration['EdgeType'],
                        'Bridge': styleconfiguration['BridgeDescription'],
                        'Hinge': styleconfiguration['Hinge'],
                        'LensType': styleconfiguration['LensDescription'],
                        'RX': styleconfiguration['RX'],
                        'ClipOnOption': styleconfiguration['ClipSunglass'],
                        'Sideshields': styleconfiguration['Sideshields'],
                        'Warranty': styleconfiguration['Warranty'],
                        'Sunglasses': styleconfiguration['ProductGroup'],
                        'ConfigurationFramesMasterID': styleconfiguration['Configurations'][0]['ConfigurationFramesMasterID'],

                        'SKU': styleconfiguration['Configurations'][0]['SKU'],

                        'Eye': styleconfiguration['Configurations'][0]['EyeSize'],
                        'Bridge': styleconfiguration['Configurations'][0]['BridgeSize'],
                        'Temple': styleconfiguration['Configurations'][0]['TempleLength'],
                        'Color': styleconfiguration['Configurations'][0]['FrameColor'],
                        'ColorCode': styleconfiguration['Configurations'][0]['FrameColorCode'],
                        'LensColor': styleconfiguration['Configurations'][0]['LensColor'],
                        'Tags': '',
                        'Discontinued': styleconfiguration['Configurations'][0]['ConfigurationStatus'],
                        'A': styleconfiguration['Configurations'][0]['A'],
                        'B': styleconfiguration['Configurations'][0]['B'],
                        'DBL': styleconfiguration['Configurations'][0]['DBL'],
                        'ED': styleconfiguration['Configurations'][0]['ED'],
                        'EDAngle': styleconfiguration['Configurations'][0]['EDAngle'],
                        'UPC': styleconfiguration['Configurations'][0]['UPC'],

                        'ChangedPrice': styleconfiguration['Configurations'][0]['ChangedPrice'],
                        'NewPrice': styleconfiguration['Configurations'][0]['NewPrice'],
                        'ConfigurationStatus': styleconfiguration['Configurations'][0]['ConfigurationStatus'],
                        'SalePrice': styleconfiguration['Configurations'][0]['CompletePrice'],
                    })
                    data[-1]['Retail'] = self.get_retail_by_wholesale(styleconfiguration['Configurations'][0]['CompletePrice'], styleconfiguration['CollectionFramesMasterID'])
                    data[-1]['json'] = json.dumps(data[-1])
                    return data
                else:
                    return []
            else:
                return 0
        except:
            raise exceptions.AccessDenied("Server error\n Please try again in few minutes")

    def check_upc_exist(self, records):
        data = []
        for record in records:
            product_product = self.env['product.product'].search([('barcode', '=', record)])
            if product_product.id:
                data.append(record)

        data_string = ''
        for record in data:
            data_string+=record + "\n"

        return 1 if len(data) else 0, data, data_string

    def import_frames(self, data, upc_data, existed_upcs):
        existed_upcs = list(set(existed_upcs))
        try:
            for style in data:
                spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].search([('mfmid', '=', int(style['ManufacturerFramesMasterID']))], limit=1)
                if not spec_frame_manufacturer_id.id:
                    spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].create({
                        'mfmid': int(style['ManufacturerFramesMasterID']),
                        'name': style['ManufacturerName'],
                    })
                spec_brand_brand_id = self.env['spec.brand.brand'].search([('bfmid', '=', int(style['BrandFramesMasterID']))], limit=1)
                if not spec_brand_brand_id.id:
                    spec_brand_brand_id = self.env['spec.brand.brand'].create({
                        'mfmid': spec_frame_manufacturer_id.id,
                        'bfmid': int(style['BrandFramesMasterID']),
                        'brand_type': 'frame',
                        'name': style['BrandName'],
                    })
                spec_collection_collection_id = self.env['spec.collection.collection'].search([('cfmid', '=', int(style['CollectionFramesMasterID']))], limit=1)
                if not spec_collection_collection_id.id:
                    spec_collection_collection_id = self.env['spec.collection.collection'].create({
                        'brand_id': spec_brand_brand_id.id,
                        'cfmid': int(style['CollectionFramesMasterID']),
                        'name': style['CollectionName'],
                    })

                spec_frame_material_id = self.env['spec.frame.material'].search([('name', '=', style['Material'])], limit=1)
                if not spec_frame_material_id.id:
                    spec_frame_material_id = self.env['spec.frame.material'].create({
                        'name': style['Material'],
                    })
                spec_shape_shape_id = self.env['spec.shape.shape'].search([('name', '=', style['Shape'])], limit=1)
                if not spec_shape_shape_id.id:
                    spec_shape_shape_id = self.env['spec.shape.shape'].create({
                        'name': style['Shape'],
                    })
                spec_gender_type_id = self.env['spec.gender.type'].search([('name', '=', style['GenderType'])], limit=1)
                if not spec_gender_type_id.id:
                    spec_gender_type_id = self.env['spec.gender.type'].create({
                        'name': style['GenderType'],
                    })
                age = ''
                if style['Age'] == 'Adult':
                    age = 'adult'
                elif style['Age'] == 'Child':
                    age = 'child'
                elif style['Age'] == 'Youth/Teen':
                    age = 'youth_teen'
                elif style['Age'] == 'Infant':
                    age = 'infant'
                elif style['Age'] == 'Child & Adult':
                    age = 'child_adult'
                spec_frame_type_id = self.env['spec.frame.type'].search([('name', '=', style['FrameType'])], limit=1)
                if not spec_frame_type_id.id:
                    spec_frame_type_id = self.env['spec.frame.type'].create({
                        'name': style['FrameType'],
                    })
                rim = ''
                if style['Rim'] == '3-Piece Compression':
                    rim = 'piece_compression'
                elif style['Rim'] == '3-Piece Screw':
                    rim = 'piece_screw'
                elif style['Rim'] == 'Full Rim':
                    rim = 'full_rim'
                elif style['Rim'] == 'Half Rim':
                    rim = 'half_Rim'
                elif style['Rim'] == 'Inverted Half Rim':
                    rim = 'inverted_half_Rim'
                elif style['Rim'] == 'None':
                    rim = 'none'
                elif style['Rim'] == 'Other':
                    rim = 'other'
                elif style['Rim'] == 'Semi-Rimless':
                    rim = 'semi_rimless'
                elif style['Rim'] == 'Shield':
                    rim = 'shield'
                edge = ''
                if style['EdgeType'] == 'drill-mount':
                    edge = 'drill_mount'
                else:
                    edge = style['EdgeType']
                bridge = ''
                if style['Bridge'] == 'Adjustable nose pads':
                    bridge = 'adjustable_nose_pads'
                elif style['Bridge'] == 'Double':
                    bridge = 'double'
                elif style['Bridge'] == 'Keyhole':
                    bridge = 'keyhole'
                elif style['Bridge'] == 'Other':
                    bridge = 'other'
                elif style['Bridge'] == 'Saddle':
                    bridge = 'saddle'
                elif style['Bridge'] == 'Single bridge':
                    bridge = 'single_Bridge'
                elif style['Bridge'] == 'Unifit':
                    bridge = 'unifit'
                elif style['Bridge'] == 'Universal':
                    bridge = 'universal'
                hinge = ''
                if style['Hinge'] == 'Hingeless':
                    hinge = 'hingeless'
                elif style['Hinge'] == 'Micro spring Hinge':
                    hinge = 'micro_spring_hinge'
                elif style['Hinge'] == 'Regular Hinge':
                    hinge = 'regular_hinge'
                elif style['Hinge'] == 'Screwless Hinge':
                    hinge = 'screwless_hinge'
                elif style['Hinge'] == 'Spring Hinge':
                    hinge = 'spring_hinge'
                spec_lenses_type_id = self.env['spec.lenses.type'].search([('name', '=', style['LensType'])], limit=1)
                if not spec_lenses_type_id.id:
                    spec_lenses_type_id = self.env['spec.lenses.type'].create({
                        'name': style['LensType'],
                    })
                rx = ''
                if style['RX'] == 'Other':
                    rx = 'other'
                elif style['RX'] == 'Prescription available & Rx adaptable.':
                    rx = 'prescription_available_adaptable'
                elif style['RX'] == 'Prescription available.':
                    rx = 'prescription_adaptable'
                elif style['RX'] == 'Rx adaptable.':
                    rx = 'rx_daptable.'
                clip = ''
                if style['ClipOnOption'] == 'Available as a Sunglass.':
                    clip = 'available_sunglass.'
                elif style['ClipOnOption'] == 'Clip-on Available':
                    clip = 'clip_available'
                elif style['ClipOnOption'] == 'Clip-on included.':
                    clip = 'clip_included'
                elif style['ClipOnOption'] == 'Magnetic clip-on available':
                    clip = 'magnetic_clip_available'
                elif style['ClipOnOption'] == 'Magnetic clip-on included.':
                    clip = 'magnetic_clip_included'
                elif style['ClipOnOption'] == 'Other':
                    clip = 'other'
                side = ''
                if style['Sideshields'] == 'Detachable':
                    side = 'detachable'
                elif style['Sideshields'] == 'Flat fold':
                    side = 'flat_fold'
                elif style['Sideshields'] == 'Other':
                    side = 'other'
                elif style['Sideshields'] == 'Permanent':
                    side = 'permanent'
                warranty = ''
                if style['Warranty'] == '1-year warranty.':
                    warranty = '1_year_arranty'
                elif style['Warranty'] == '2-year warranty.':
                    warranty = '2_year_arranty'
                elif style['Warranty'] == '3-year warranty.':
                    warranty = '3_year_arranty'
                elif style['Warranty'] == 'Lifetime warranty on manufacturer’s defects':
                    warranty = 'lifetime_year_arranty'
                elif style['Warranty'] == 'Material defects or workmanship: 12 month warranty.':
                    warranty = '12_year_arranty'
                elif style['Warranty'] == 'Material defects or workmanship: 24 month warranty.':
                    warranty = '24_year_arranty'
                elif style['Warranty'] == 'Other':
                    warranty = 'other'
                elif style['Warranty'] == 'Unconditional lifetime warranty.':
                    warranty = 'unconditional_year_arranty'

                product_template_id = self.env['product.template'].search([('collection_id', '=', spec_collection_collection_id.id),
                                                                        ('frame_manufacturer_id', '=', spec_frame_manufacturer_id.id),
                                                                        ('brand_id', '=', spec_brand_brand_id.id),
                                                                        ('sfmid', '=', int(style['StyleFramesMasterID']))
                                                                        ], limit=1)
                if not product_template_id.id:
                    product_category_id = self.env['product.category'].search([('name', '=', 'Frames')], limit=1)
                    if not product_category_id.id:
                        product_category_id = self.env['product.category'].create({
                            'name': 'Frames'
                        })
                    product_template_id = self.env['product.template'].with_context(disable_varients=True, create_product_product=False).create({
                        'type': 'product',
                        'frame_manufacturer_id': spec_frame_manufacturer_id.id,
                        'brand_id': spec_brand_brand_id.id,
                        'collection_id': spec_collection_collection_id.id,
                        'sfmid': int(style['StyleFramesMasterID']),
                        'model_number': style['StyleName'],
                        'name': spec_collection_collection_id.name + " " + style['StyleName'],
                        'material_frame_id': spec_frame_material_id.id,
                        'shap_id': spec_shape_shape_id.id,
                        'gender_ids': spec_gender_type_id.id,
                        'age': age if age != '' else None,
                        'frame_type_id': spec_frame_type_id.id,
                        'rim': rim if rim != '' else None,
                        'edge_type': edge if edge != '' else None,
                        'bridge_fix': bridge if bridge != '' else None,
                        'hinge': hinge if hinge != '' else None,
                        'lenses': spec_lenses_type_id.id,
                        'rx': rx if rx != '' else None,
                        'clip_on_option': clip if clip != '' else None,
                        'side_shields': side if side != '' else None,
                        'warranty': warranty if warranty != '' else None,
                        'is_sunclass': True if style['Sunglasses'] == 'Sunglasses' else False,
                        'categ_id': product_category_id.id,
                        'discontinue': True if style['StyleStatus'] == 'D' else False,
                        'discont_date': fields.datetime.strptime(style['StyleDiscontinuedOn'],'%m/%d/%Y') if style['StyleStatus'] == 'D' else None,
                        'frames_data_last_sync': fields.datetime.now().date(),
                        'list_price': float(style['Retail']) if style['Retail'] else 0,
                        'wholesale_cost': float(style['Wholesale']) if style['Wholesale'] else 0,
                    })
                    for configuration in style['configurations']:
                        if configuration["UPC"] not in existed_upcs and self.env['product.product'].search_count([('barcode', '=', configuration['UPC'])]) == 0:
                            spec_color_family_id = self.env['spec.color.family'].search([('name', '=', configuration['Color'])], limit=1)
                            if not spec_color_family_id.id:
                                spec_color_family_id = self.env['spec.color.family'].create({
                                    'name': configuration['Color'],
                                })
                            spec_color_code_family_id = self.env['spec.color.code.family'].search([('name', '=', configuration['ColorCode'])], limit=1)
                            if not spec_color_code_family_id.id:
                                spec_color_code_family_id = self.env['spec.color.code.family'].create({
                                    'name': configuration['ColorCode'],
                                })
                            spec_lens_colors_id = self.env['spec.lens.colors'].search([('name', '=', configuration['LensColor'])], limit=1)
                            if not spec_lens_colors_id.id:
                                spec_lens_colors_id = self.env['spec.lens.colors'].create({
                                    'name': configuration['LensColor'],
                                })
                            product_product_id = self.env['product.product'].with_context(disable_varients=True, create_product_product=False).create({
                                # 'name': spec_collection_collection_id.name + " " + style['StyleName'] + "(" + configuration['UPC'] + ")",
                                'eye': configuration['Eye'],
                                'bridge': configuration['Bridge'],
                                'temple': configuration['Temple'],
                                'color_id': spec_color_family_id.id,
                                'color_code_id': spec_color_code_family_id.id,
                                'lens_color_id': spec_lens_colors_id.id,
                                'a': float(configuration['A']) if configuration['A'] else 0,
                                'b': float(configuration['B']) if configuration['B'] else 0,
                                'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                                'ed': float(configuration['ED']) if configuration['ED'] else 0,
                                'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                                'barcode': configuration['UPC'],
                                'default_code': configuration['SKU'],
                                # 'list_price': float(configuration['Retail']) if configuration['Retail'] else 0,
                                'product_min_qty': float(configuration['Min_Qty']) if configuration['Min_Qty'] else 0,
                                'product_max_qty': float(configuration['Max_Qty']) if configuration['Max_Qty'] else 0,
                                'product_tmpl_id': product_template_id.id,
                                'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                                'list_price': float(configuration['Retail']) if configuration['Retail'] else (float(style['Retail']) if style['Retail'] else float(configuration['SalePrice'])),
                                'configurations_last_modified_on': fields.datetime.now().date(),
                            })
                if style['Vendor'] and style['Vendor'] != '0':
                    product_supplierinfo = self.env['product.supplierinfo'].create({
                        'name': style['Vendor'],
                        # 'product_id': product_product_id.id,
                        'min_qty': 1,
                        'wholesale_cost': float(style['Wholesale']),
                        'price': float(style['Wholesale']),
                        'product_tmpl_id': product_template_id.id,
                    })
                        # else:
                        #     if configuration["UPC"] not in existed_upcs:
                        #         existed_upcsted_upcs.append(configuration["UPC"]);

            for style in upc_data:
                configuration = style
                if configuration["UPC"] not in existed_upcs and self.env['product.product'].search_count([('barcode', '=', configuration['UPC'])]) == 0:
                    spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].search([('mfmid', '=', int(style['ManufacturerFramesMasterID']))], limit=1)
                    if not spec_frame_manufacturer_id.id:
                        spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].create({
                            'mfmid': int(style['ManufacturerFramesMasterID']),
                            'name': style['ManufacturerName'],
                        })
                    spec_brand_brand_id = self.env['spec.brand.brand'].search([('bfmid', '=', int(style['BrandFramesMasterID']))], limit=1)
                    if not spec_brand_brand_id.id:
                        spec_brand_brand_id = self.env['spec.brand.brand'].create({
                            'mfmid': spec_frame_manufacturer_id.id,
                            'bfmid': int(style['BrandFramesMasterID']),
                            'brand_type': 'frame',
                            'name': style['BrandName'],
                        })
                    spec_collection_collection_id = self.env['spec.collection.collection'].search([('cfmid', '=', int(style['CollectionFramesMasterID']))], limit=1)
                    if not spec_collection_collection_id.id:
                        spec_collection_collection_id = self.env['spec.collection.collection'].create({
                            'brand_id': spec_brand_brand_id.id,
                            'cfmid': int(style['CollectionFramesMasterID']),
                            'name': style['CollectionName'],
                        })

                    spec_frame_material_id = self.env['spec.frame.material'].search([('name', '=', style['Material'])], limit=1)
                    if not spec_frame_material_id.id:
                        spec_frame_material_id = self.env['spec.frame.material'].create({
                            'name': style['Material'],
                        })
                    spec_shape_shape_id = self.env['spec.shape.shape'].search([('name', '=', style['Shape'])], limit=1)
                    if not spec_shape_shape_id.id:
                        spec_shape_shape_id = self.env['spec.shape.shape'].create({
                            'name': style['Shape'],
                        })
                    spec_gender_type_id = self.env['spec.gender.type'].search([('name', '=', style['GenderType'])], limit=1)
                    if not spec_gender_type_id.id:
                        spec_gender_type_id = self.env['spec.gender.type'].create({
                            'name': style['GenderType'],
                        })
                    age = ''
                    if style['Age'] == 'Adult':
                        age = 'adult'
                    elif style['Age'] == 'Child':
                        age = 'child'
                    elif style['Age'] == 'Youth/Teen':
                        age = 'youth_teen'
                    elif style['Age'] == 'Infant':
                        age = 'infant'
                    elif style['Age'] == 'Child & Adult':
                        age = 'child_adult'
                    spec_frame_type_id = self.env['spec.frame.type'].search([('name', '=', style['FrameType'])], limit=1)
                    if not spec_frame_type_id.id:
                        spec_frame_type_id = self.env['spec.frame.type'].create({
                            'name': style['FrameType'],
                        })
                    rim = ''
                    if style['Rim'] == '3-Piece Compression':
                        rim = 'piece_compression'
                    elif style['Rim'] == '3-Piece Screw':
                        rim = 'piece_screw'
                    elif style['Rim'] == 'Full Rim':
                        rim = 'full_rim'
                    elif style['Rim'] == 'Half Rim':
                        rim = 'half_Rim'
                    elif style['Rim'] == 'Inverted Half Rim':
                        rim = 'inverted_half_Rim'
                    elif style['Rim'] == 'None':
                        rim = 'none'
                    elif style['Rim'] == 'Other':
                        rim = 'other'
                    elif style['Rim'] == 'Semi-Rimless':
                        rim = 'semi_rimless'
                    elif style['Rim'] == 'Shield':
                        rim = 'shield'
                    edge = ''
                    if style['EdgeType'] == 'drill-mount':
                        edge = 'drill_mount'
                    else:
                        edge = style['EdgeType']
                    bridge = ''
                    if style['Bridge'] == 'Adjustable nose pads':
                        bridge = 'adjustable_nose_pads'
                    elif style['Bridge'] == 'Double':
                        bridge = 'double'
                    elif style['Bridge'] == 'Keyhole':
                        bridge = 'keyhole'
                    elif style['Bridge'] == 'Other':
                        bridge = 'other'
                    elif style['Bridge'] == 'Saddle':
                        bridge = 'saddle'
                    elif style['Bridge'] == 'Single bridge':
                        bridge = 'single_Bridge'
                    elif style['Bridge'] == 'Unifit':
                        bridge = 'unifit'
                    elif style['Bridge'] == 'Universal':
                        bridge = 'universal'
                    hinge = ''
                    if style['Hinge'] == 'Hingeless':
                        hinge = 'hingeless'
                    elif style['Hinge'] == 'Micro spring Hinge':
                        hinge = 'micro_spring_hinge'
                    elif style['Hinge'] == 'Regular Hinge':
                        hinge = 'regular_hinge'
                    elif style['Hinge'] == 'Screwless Hinge':
                        hinge = 'screwless_hinge'
                    elif style['Hinge'] == 'Spring Hinge':
                        hinge = 'spring_hinge'
                    spec_lenses_type_id = self.env['spec.lenses.type'].search([('name', '=', style['LensType'])], limit=1)
                    if not spec_lenses_type_id.id:
                        spec_lenses_type_id = self.env['spec.lenses.type'].create({
                            'name': style['LensType'],
                        })
                    rx = ''
                    if style['RX'] == 'Other':
                        rx = 'other'
                    elif style['RX'] == 'Prescription available & Rx adaptable.':
                        rx = 'prescription_available_adaptable'
                    elif style['RX'] == 'Prescription available.':
                        rx = 'prescription_adaptable'
                    elif style['RX'] == 'Rx adaptable.':
                        rx = 'rx_daptable.'
                    clip = ''
                    if style['ClipOnOption'] == 'Available as a Sunglass.':
                        clip = 'available_sunglass.'
                    elif style['ClipOnOption'] == 'Clip-on Available':
                        clip = 'clip_available'
                    elif style['ClipOnOption'] == 'Clip-on included.':
                        clip = 'clip_included'
                    elif style['ClipOnOption'] == 'Magnetic clip-on available':
                        clip = 'magnetic_clip_available'
                    elif style['ClipOnOption'] == 'Magnetic clip-on included.':
                        clip = 'magnetic_clip_included'
                    elif style['ClipOnOption'] == 'Other':
                        clip = 'other'
                    side = ''
                    if style['Sideshields'] == 'Detachable':
                        side = 'detachable'
                    elif style['Sideshields'] == 'Flat fold':
                        side = 'flat_fold'
                    elif style['Sideshields'] == 'Other':
                        side = 'other'
                    elif style['Sideshields'] == 'Permanent':
                        side = 'permanent'
                    warranty = ''
                    if style['Warranty'] == '1-year warranty.':
                        warranty = '1_year_arranty'
                    elif style['Warranty'] == '2-year warranty.':
                        warranty = '2_year_arranty'
                    elif style['Warranty'] == '3-year warranty.':
                        warranty = '3_year_arranty'
                    elif style['Warranty'] == 'Lifetime warranty on manufacturer’s defects':
                        warranty = 'lifetime_year_arranty'
                    elif style['Warranty'] == 'Material defects or workmanship: 12 month warranty.':
                        warranty = '12_year_arranty'
                    elif style['Warranty'] == 'Material defects or workmanship: 24 month warranty.':
                        warranty = '24_year_arranty'
                    elif style['Warranty'] == 'Other':
                        warranty = 'other'
                    elif style['Warranty'] == 'Unconditional lifetime warranty.':
                        warranty = 'unconditional_year_arranty'

                    product_template_id = self.env['product.template'].search([('collection_id', '=', spec_collection_collection_id.id),
                                                                            ('frame_manufacturer_id', '=', spec_frame_manufacturer_id.id),
                                                                            ('brand_id', '=', spec_brand_brand_id.id),
                                                                            ('sfmid', '=', int(style['StyleFramesMasterID']))
                                                                            ], limit=1)
                    if not product_template_id.id:
                        product_template_id = self.env['product.template'].with_context(disable_varients=True, create_product_product=False).create({
                            'type': 'product',
                            'frame_manufacturer_id': spec_frame_manufacturer_id.id,
                            'brand_id': spec_brand_brand_id.id,
                            'collection_id': spec_collection_collection_id.id,
                            'sfmid': int(style['StyleFramesMasterID']),
                            'model_number': style['StyleName'],
                            'name': spec_collection_collection_id.name + " " + style['StyleName'],
                            'material_frame_id': spec_frame_material_id.id,
                            'shap_id': spec_shape_shape_id.id,
                            'gender_ids': spec_gender_type_id.id,
                            'age': age if age != '' else None,
                            'frame_type_id': spec_frame_type_id.id,
                            'rim': rim if rim != '' else None,
                            'edge_type': edge if edge != '' else None,
                            'bridge_fix': bridge if bridge != '' else None,
                            'hinge': hinge if hinge != '' else None,
                            'lenses': spec_lenses_type_id.id,
                            'rx': rx if rx != '' else None,
                            'clip_on_option': clip if clip != '' else None,
                            'side_shields': side if side != '' else None,
                            'warranty': warranty if warranty != '' else None,
                            'is_sunclass': True if style['Sunglasses'] == 'Sunglasses' else False,
                            'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                            'discontinue': True if style['StyleStatus'] == 'D' else False,
                            'discont_date': fields.datetime.strptime(style['StyleDiscontinuedOn'],'%m/%d/%Y') if style['StyleStatus'] == 'D' else None,
                            'frames_data_last_sync': fields.datetime.now().date(),
                            'list_price': float(style['Retail']) if style['Retail'] else 0,
                            'wholesale_cost': float(style['Wholesale']) if style['Wholesale'] else 0,
                        })
                    spec_color_family_id = self.env['spec.color.family'].search([('name', '=', configuration['Color'])], limit=1)
                    if not spec_color_family_id.id:
                        spec_color_family_id = self.env['spec.color.family'].create({
                            'name': configuration['Color'],
                        })
                    spec_color_code_family_id = self.env['spec.color.code.family'].search([('name', '=', configuration['ColorCode'])], limit=1)
                    if not spec_color_code_family_id.id:
                        spec_color_code_family_id = self.env['spec.color.code.family'].create({
                            'name': configuration['ColorCode'],
                        })
                    spec_lens_colors_id = self.env['spec.lens.colors'].search([('name', '=', configuration['LensColor'])], limit=1)
                    if not spec_lens_colors_id.id:
                        spec_lens_colors_id = self.env['spec.lens.colors'].create({
                            'name': configuration['LensColor'],
                        })

                    product_product_id = self.env['product.product'].with_context(disable_varients=True, create_product_product=False).create({
                        # 'name': spec_collection_collection_id.name + " " + style['StyleName'] + "(" + configuration['UPC'] + ")",
                        'eye': configuration['Eye'],
                        'bridge': configuration['Bridge'],
                        'temple': configuration['Temple'],
                        'color_id': spec_color_family_id.id,
                        'color_code_id': spec_color_code_family_id.id,
                        'lens_color_id': spec_lens_colors_id.id,
                        'a': float(configuration['A']) if configuration['A'] else 0,
                        'b': float(configuration['B']) if configuration['B'] else 0,
                        'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                        'ed': float(configuration['ED']) if configuration['ED'] else 0,
                        'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                        'barcode': configuration['UPC'],
                        'default_code': configuration['SKU'],
                        # 'list_price': float(configuration['Retail']) if configuration['Retail'] else 0,
                        'product_min_qty': float(configuration['Min_Qty']) if configuration['Min_Qty'] else 0,
                        'product_max_qty': float(configuration['Max_Qty']) if configuration['Max_Qty'] else 0,
                        'product_tmpl_id': product_template_id.id,
                        'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                        'list_price': float(style['Retail']) if style['Retail'] else float(configuration['SalePrice']),
                        'configurations_last_modified_on': fields.datetime.now().date(),
                    })
                    if style['Vendor'] and style['Vendor'] != '0':
                        product_supplierinfo = self.env['product.supplierinfo'].create({
                            'name': style['Vendor'],
                            # 'product_id': product_product_id.id,
                            'min_qty': 1,
                            'wholesale_cost': float(configuration['SalePrice']),
                            'price': float(configuration['SalePrice']),
                            'product_tmpl_id': product_template_id.id,
                        })
                    self.env['product.template'].fd_synchronize(product_template_id,product_template_id)
                else:
                    spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].search([('mfmid', '=', int(style['ManufacturerFramesMasterID']))], limit=1)
                    if not spec_frame_manufacturer_id.id:
                        spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].create({
                            'mfmid': int(style['ManufacturerFramesMasterID']),
                            'name': style['ManufacturerName'],
                        })
                    spec_brand_brand_id = self.env['spec.brand.brand'].search([('bfmid', '=', int(style['BrandFramesMasterID']))], limit=1)
                    if not spec_brand_brand_id.id:
                        spec_brand_brand_id = self.env['spec.brand.brand'].create({
                            'mfmid': spec_frame_manufacturer_id.id,
                            'bfmid': int(style['BrandFramesMasterID']),
                            'brand_type': 'frame',
                            'name': style['BrandName'],
                        })
                    spec_collection_collection_id = self.env['spec.collection.collection'].search([('cfmid', '=', int(style['CollectionFramesMasterID']))], limit=1)
                    if not spec_collection_collection_id.id:
                        spec_collection_collection_id = self.env['spec.collection.collection'].create({
                            'brand_id': spec_brand_brand_id.id,
                            'cfmid': int(style['CollectionFramesMasterID']),
                            'name': style['CollectionName'],
                        })
                    product_template_id = self.env['product.template'].search([('collection_id', '=', spec_collection_collection_id.id),
                                                                               ('frame_manufacturer_id', '=', spec_frame_manufacturer_id.id),
                                                                               ('brand_id', '=', spec_brand_brand_id.id),
                                                                               ('sfmid', '=', int(style['StyleFramesMasterID']))
                                                                              ], limit=1)
                    if product_template_id.id:
                        self.env['product.template'].fd_synchronize(product_template_id, product_template_id)

            return True, existed_upcs
        except Exception as e:
            raise (e)
            print(e)
            return False, existed_upcs

    def sync_frames(self, data, upc_data):
        try:
            for style in data:
                spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].search([('mfmid', '=', int(style['ManufacturerFramesMasterID']))], limit=1)
                if not spec_frame_manufacturer_id.id:
                    spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].create({
                        'mfmid': int(style['ManufacturerFramesMasterID']),
                        'name': style['ManufacturerName'],
                    })
                spec_brand_brand_id = self.env['spec.brand.brand'].search([('bfmid', '=', int(style['BrandFramesMasterID']))], limit=1)
                if not spec_brand_brand_id.id:
                    spec_brand_brand_id = self.env['spec.brand.brand'].create({
                        'mfmid': spec_frame_manufacturer_id.id,
                        'bfmid': int(style['BrandFramesMasterID']),
                        'brand_type': 'frame',
                        'name': style['BrandName'],
                    })
                spec_collection_collection_id = self.env['spec.collection.collection'].search([('cfmid', '=', int(style['CollectionFramesMasterID']))], limit=1)
                if not spec_collection_collection_id.id:
                    spec_collection_collection_id = self.env['spec.collection.collection'].create({
                        'brand_id': spec_brand_brand_id.id,
                        'cfmid': int(style['CollectionFramesMasterID']),
                        'name': style['CollectionName'],
                    })

                spec_frame_material_id = self.env['spec.frame.material'].search([('name', '=', style['Material'])], limit=1)
                if not spec_frame_material_id.id:
                    spec_frame_material_id = self.env['spec.frame.material'].create({
                        'name': style['Material'],
                    })
                spec_shape_shape_id = self.env['spec.shape.shape'].search([('name', '=', style['Shape'])], limit=1)
                if not spec_shape_shape_id.id:
                    spec_shape_shape_id = self.env['spec.shape.shape'].create({
                        'name': style['Shape'],
                    })
                spec_gender_type_id = self.env['spec.gender.type'].search([('name', '=', style['GenderType'])], limit=1)
                if not spec_gender_type_id.id:
                    spec_gender_type_id = self.env['spec.gender.type'].create({
                        'name': style['GenderType'],
                    })
                age = ''
                if style['Age'] == 'Adult':
                    age = 'adult'
                elif style['Age'] == 'Child':
                    age = 'child'
                elif style['Age'] == 'Youth/Teen':
                    age = 'youth_teen'
                elif style['Age'] == 'Infant':
                    age = 'infant'
                elif style['Age'] == 'Child & Adult':
                    age = 'child_adult'
                spec_frame_type_id = self.env['spec.frame.type'].search([('name', '=', style['FrameType'])], limit=1)
                if not spec_frame_type_id.id:
                    spec_frame_type_id = self.env['spec.frame.type'].create({
                        'name': style['FrameType'],
                    })
                rim = ''
                if style['Rim'] == '3-Piece Compression':
                    rim = 'piece_compression'
                elif style['Rim'] == '3-Piece Screw':
                    rim = 'piece_screw'
                elif style['Rim'] == 'Full Rim':
                    rim = 'full_rim'
                elif style['Rim'] == 'Half Rim':
                    rim = 'half_Rim'
                elif style['Rim'] == 'Inverted Half Rim':
                    rim = 'inverted_half_Rim'
                elif style['Rim'] == 'None':
                    rim = 'none'
                elif style['Rim'] == 'Other':
                    rim = 'other'
                elif style['Rim'] == 'Semi-Rimless':
                    rim = 'semi_rimless'
                elif style['Rim'] == 'Shield':
                    rim = 'shield'
                edge = ''
                if style['EdgeType'] == 'drill-mount':
                    edge = 'drill_mount'
                else:
                    edge = style['EdgeType']
                bridge = ''
                if style['Bridge'] == 'Adjustable nose pads':
                    bridge = 'adjustable_nose_pads'
                elif style['Bridge'] == 'Double':
                    bridge = 'double'
                elif style['Bridge'] == 'Keyhole':
                    bridge = 'keyhole'
                elif style['Bridge'] == 'Other':
                    bridge = 'other'
                elif style['Bridge'] == 'Saddle':
                    bridge = 'saddle'
                elif style['Bridge'] == 'Single bridge':
                    bridge = 'single_Bridge'
                elif style['Bridge'] == 'Unifit':
                    bridge = 'unifit'
                elif style['Bridge'] == 'Universal':
                    bridge = 'universal'
                hinge = ''
                if style['Hinge'] == 'Hingeless':
                    hinge = 'hingeless'
                elif style['Hinge'] == 'Micro spring Hinge':
                    hinge = 'micro_spring_hinge'
                elif style['Hinge'] == 'Regular Hinge':
                    hinge = 'regular_hinge'
                elif style['Hinge'] == 'Screwless Hinge':
                    hinge = 'screwless_hinge'
                elif style['Hinge'] == 'Spring Hinge':
                    hinge = 'spring_hinge'
                spec_lenses_type_id = self.env['spec.lenses.type'].search([('name', '=', style['LensType'])], limit=1)
                if not spec_lenses_type_id.id:
                    spec_lenses_type_id = self.env['spec.lenses.type'].create({
                        'name': style['LensType'],
                    })
                rx = ''
                if style['RX'] == 'Other':
                    rx = 'other'
                elif style['RX'] == 'Prescription available & Rx adaptable.':
                    rx = 'prescription_available_adaptable'
                elif style['RX'] == 'Prescription available.':
                    rx = 'prescription_adaptable'
                elif style['RX'] == 'Rx adaptable.':
                    rx = 'rx_daptable.'
                clip = ''
                if style['ClipOnOption'] == 'Available as a Sunglass.':
                    clip = 'available_sunglass.'
                elif style['ClipOnOption'] == 'Clip-on Available':
                    clip = 'clip_available'
                elif style['ClipOnOption'] == 'Clip-on included.':
                    clip = 'clip_included'
                elif style['ClipOnOption'] == 'Magnetic clip-on available':
                    clip = 'magnetic_clip_available'
                elif style['ClipOnOption'] == 'Magnetic clip-on included.':
                    clip = 'magnetic_clip_included'
                elif style['ClipOnOption'] == 'Other':
                    clip = 'other'
                side = ''
                if style['Sideshields'] == 'Detachable':
                    side = 'detachable'
                elif style['Sideshields'] == 'Flat fold':
                    side = 'flat_fold'
                elif style['Sideshields'] == 'Other':
                    side = 'other'
                elif style['Sideshields'] == 'Permanent':
                    side = 'permanent'
                warranty = ''
                if style['Warranty'] == '1-year warranty.':
                    warranty = '1_year_arranty'
                elif style['Warranty'] == '2-year warranty.':
                    warranty = '2_year_arranty'
                elif style['Warranty'] == '3-year warranty.':
                    warranty = '3_year_arranty'
                elif style['Warranty'] == 'Lifetime warranty on manufacturer’s defects':
                    warranty = 'lifetime_year_arranty'
                elif style['Warranty'] == 'Material defects or workmanship: 12 month warranty.':
                    warranty = '12_year_arranty'
                elif style['Warranty'] == 'Material defects or workmanship: 24 month warranty.':
                    warranty = '24_year_arranty'
                elif style['Warranty'] == 'Other':
                    warranty = 'other'
                elif style['Warranty'] == 'Unconditional lifetime warranty.':
                    warranty = 'unconditional_year_arranty'

                product_template_id = self.env['product.template'].search([('collection_id', '=', spec_collection_collection_id.id),
                                                                        ('frame_manufacturer_id', '=', spec_frame_manufacturer_id.id),
                                                                        ('brand_id', '=', spec_brand_brand_id.id),
                                                                        ('sfmid', '=', int(style['StyleFramesMasterID']))
                                                                        ], limit=1)
                if not product_template_id.id:
                    product_template_id = self.env['product.template'].with_context(disable_varients=True, create_product_product=False).create({
                        'type': 'product',
                        'frame_manufacturer_id': spec_frame_manufacturer_id.id,
                        'brand_id': spec_brand_brand_id.id,
                        'collection_id': spec_collection_collection_id.id,
                        'sfmid': int(style['StyleFramesMasterID']),
                        'model_number': style['StyleName'],
                        'name': spec_collection_collection_id.name + " " + style['StyleName'],
                        'material_frame_id': spec_frame_material_id.id,
                        'shap_id': spec_shape_shape_id.id,
                        'gender_ids': spec_gender_type_id.id,
                        'age': age if age != '' else None,
                        'frame_type_id': spec_frame_type_id.id,
                        'rim': rim if rim != '' else None,
                        'edge_type': edge if edge != '' else None,
                        'bridge_fix': bridge if bridge != '' else None,
                        'hinge': hinge if hinge != '' else None,
                        'lenses': spec_lenses_type_id.id,
                        'rx': rx if rx != '' else None,
                        'clip_on_option': clip if clip != '' else None,
                        'side_shields': side if side != '' else None,
                        'warranty': warranty if warranty != '' else None,
                        'is_sunclass': True if style['Sunglasses'] == 'Sunglasses' else False,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                        'discontinue': True if style['StyleStatus'] == 'D' else False,
                        'discont_date': fields.datetime.strptime(style['StyleDiscontinuedOn'],'%m/%d/%Y') if style['StyleStatus'] == 'D' else None,
                        'frames_data_last_sync': fields.datetime.now().date(),
                        'list_price': float(configuration['Retail']) if configuration['Retail'] else (float(style['Retail']) if style['Retail'] else float(configuration['SalePrice'])),
                        'wholesale_cost': float(style['Wholesale']) if style['Wholesale'] else 0,
                    })
                else:
                    product_template_id.update({
                        'material_frame_id': spec_frame_material_id.id,
                        'shap_id': spec_shape_shape_id.id,
                        'gender_ids': spec_gender_type_id.id,
                        'age': age if age != '' else None,
                        'frame_type_id': spec_frame_type_id.id,
                        'rim': rim if rim != '' else None,
                        'edge_type': edge if edge != '' else None,
                        'bridge_fix': bridge if bridge != '' else None,
                        'hinge': hinge if hinge != '' else None,
                        'lenses': spec_lenses_type_id.id,
                        'rx': rx if rx != '' else None,
                        'clip_on_option': clip if clip != '' else None,
                        'side_shields': side if side != '' else None,
                        'warranty': warranty if warranty != '' else None,
                        'is_sunclass': True if style['Sunglasses'] == 'Sunglasses' else False,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                        'discontinue': True if style['StyleStatus'] == 'D' else False,
                        'discont_date': fields.datetime.strptime(style['StyleDiscontinuedOn'],'%m/%d/%Y') if style['StyleStatus'] == 'D' else None,
                        'frames_data_last_sync': fields.datetime.now().date(),
                        'list_price': float(configuration['Retail']) if configuration['Retail'] else (
                            float(style['Retail']) if style['Retail'] else float(configuration['SalePrice'])),
                        'wholesale_cost': float(style['Wholesale']) if style['Wholesale'] else 0,
                    })

                for configuration in style['configurations']:
                    spec_color_family_id = self.env['spec.color.family'].search([('name', '=', configuration['Color'])], limit=1)
                    if not spec_color_family_id.id:
                        spec_color_family_id = self.env['spec.color.family'].create({
                            'name': configuration['Color'],
                        })
                    spec_color_code_family_id = self.env['spec.color.code.family'].search([('name', '=', configuration['ColorCode'])], limit=1)
                    if not spec_color_code_family_id.id:
                        spec_color_code_family_id = self.env['spec.color.code.family'].create({
                            'name': configuration['ColorCode'],
                        })
                    spec_lens_colors_id = self.env['spec.lens.colors'].search([('name', '=', configuration['LensColor'])], limit=1)
                    if not spec_lens_colors_id.id:
                        spec_lens_colors_id = self.env['spec.lens.colors'].create({
                            'name': configuration['LensColor'],
                        })
                    product_product_id = self.env['product.product'].search([('barcode', '=', configuration['UPC'])], limit=1)
                    if product_product_id:
                        product_product_id.update({
                            'eye': configuration['Eye'],
                            'bridge': configuration['Bridge'],
                            'temple': configuration['Temple'],
                            'color_id': spec_color_family_id.id,
                            'color_code_id': spec_color_code_family_id.id,
                            'lens_color_id': spec_lens_colors_id.id,
                            'a': float(configuration['A']) if configuration['A'] else 0,
                            'b': float(configuration['B']) if configuration['B'] else 0,
                            'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                            'ed': float(configuration['ED']) if configuration['ED'] else 0,
                            'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                            'barcode': configuration['UPC'],
                            'default_code': configuration['SKU'],
                            # 'list_price': float(configuration['Retail']) if configuration['Retail'] else 0,
                            'product_min_qty': float(configuration['Min_Qty']) if configuration['Min_Qty'] else 0,
                            'product_max_qty': float(configuration['Max_Qty']) if configuration['Max_Qty'] else 0,
                            'product_tmpl_id': product_template_id.id,
                            'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                            'list_price': float(style['Retail']) if style['Retail'] else float(configuration['SalePrice']),
                            'configurations_last_modified_on': fields.datetime.now().date(),
                        })
                    else:
                        product_product_id = self.env['product.product'].with_context(disable_varients=True, create_product_product=False).create({
                            # 'name': spec_collection_collection_id.name + " " + style['StyleName'] + "(" + configuration['UPC'] + ")",
                            'eye': configuration['Eye'],
                            'bridge': configuration['Bridge'],
                            'temple': configuration['Temple'],
                            'color_id': spec_color_family_id.id,
                            'color_code_id': spec_color_code_family_id.id,
                            'lens_color_id': spec_lens_colors_id.id,
                            'a': float(configuration['A']) if configuration['A'] else 0,
                            'b': float(configuration['B']) if configuration['B'] else 0,
                            'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                            'ed': float(configuration['ED']) if configuration['ED'] else 0,
                            'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                            'barcode': configuration['UPC'],
                            'default_code': configuration['SKU'],
                            # 'list_price': float(configuration['Retail']) if configuration['Retail'] else 0,
                            'product_min_qty': float(configuration['Min_Qty']) if configuration['Min_Qty'] else 0,
                            'product_max_qty': float(configuration['Max_Qty']) if configuration['Max_Qty'] else 0,
                            'product_tmpl_id': product_template_id.id,
                            'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                            'list_price': float(style['Retail']) if style['Retail'] else float(configuration['SalePrice']),
                            'configurations_last_modified_on': fields.datetime.now().date(),
                        })
                if style['Vendor'] and style['Vendor'] != '0':
                    product_supplierinfo = self.env['product.supplierinfo'].create({
                        'name': style['Vendor'],
                        # 'product_id': product_product_id.id,
                        'min_qty': 1,
                        'wholesale_cost': float(style['Wholesale']),
                        'price': float(style['Wholesale']),
                        'product_tmpl_id': product_template_id.id,
                    })

            for style in upc_data:
                configuration = style
                spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].search([('mfmid', '=', int(style['ManufacturerFramesMasterID']))], limit=1)
                if not spec_frame_manufacturer_id.id:
                    spec_frame_manufacturer_id = self.env['spec.frame.manufacturer'].create({
                        'mfmid': int(style['ManufacturerFramesMasterID']),
                        'name': style['ManufacturerName'],
                    })
                spec_brand_brand_id = self.env['spec.brand.brand'].search([('bfmid', '=', int(style['BrandFramesMasterID']))], limit=1)
                if not spec_brand_brand_id.id:
                    spec_brand_brand_id = self.env['spec.brand.brand'].create({
                        'mfmid': spec_frame_manufacturer_id.id,
                        'bfmid': int(style['BrandFramesMasterID']),
                        'brand_type': 'frame',
                        'name': style['BrandName'],
                    })
                spec_collection_collection_id = self.env['spec.collection.collection'].search([('cfmid', '=', int(style['CollectionFramesMasterID']))], limit=1)
                if not spec_collection_collection_id.id:
                    spec_collection_collection_id = self.env['spec.collection.collection'].create({
                        'brand_id': spec_brand_brand_id.id,
                        'cfmid': int(style['CollectionFramesMasterID']),
                        'name': style['CollectionName'],
                    })

                spec_frame_material_id = self.env['spec.frame.material'].search([('name', '=', style['Material'])], limit=1)
                if not spec_frame_material_id.id:
                    spec_frame_material_id = self.env['spec.frame.material'].create({
                        'name': style['Material'],
                    })
                spec_shape_shape_id = self.env['spec.shape.shape'].search([('name', '=', style['Shape'])], limit=1)
                if not spec_shape_shape_id.id:
                    spec_shape_shape_id = self.env['spec.shape.shape'].create({
                        'name': style['Shape'],
                    })
                spec_gender_type_id = self.env['spec.gender.type'].search([('name', '=', style['GenderType'])], limit=1)
                if not spec_gender_type_id.id:
                    spec_gender_type_id = self.env['spec.gender.type'].create({
                        'name': style['GenderType'],
                    })
                age = ''
                if style['Age'] == 'Adult':
                    age = 'adult'
                elif style['Age'] == 'Child':
                    age = 'child'
                elif style['Age'] == 'Youth/Teen':
                    age = 'youth_teen'
                elif style['Age'] == 'Infant':
                    age = 'infant'
                elif style['Age'] == 'Child & Adult':
                    age = 'child_adult'
                spec_frame_type_id = self.env['spec.frame.type'].search([('name', '=', style['FrameType'])], limit=1)
                if not spec_frame_type_id.id:
                    spec_frame_type_id = self.env['spec.frame.type'].create({
                        'name': style['FrameType'],
                    })
                rim = ''
                if style['Rim'] == '3-Piece Compression':
                    rim = 'piece_compression'
                elif style['Rim'] == '3-Piece Screw':
                    rim = 'piece_screw'
                elif style['Rim'] == 'Full Rim':
                    rim = 'full_rim'
                elif style['Rim'] == 'Half Rim':
                    rim = 'half_Rim'
                elif style['Rim'] == 'Inverted Half Rim':
                    rim = 'inverted_half_Rim'
                elif style['Rim'] == 'None':
                    rim = 'none'
                elif style['Rim'] == 'Other':
                    rim = 'other'
                elif style['Rim'] == 'Semi-Rimless':
                    rim = 'semi_rimless'
                elif style['Rim'] == 'Shield':
                    rim = 'shield'
                edge = ''
                if style['EdgeType'] == 'drill-mount':
                    edge = 'drill_mount'
                else:
                    edge = style['EdgeType']
                bridge = ''
                if style['Bridge'] == 'Adjustable nose pads':
                    bridge = 'adjustable_nose_pads'
                elif style['Bridge'] == 'Double':
                    bridge = 'double'
                elif style['Bridge'] == 'Keyhole':
                    bridge = 'keyhole'
                elif style['Bridge'] == 'Other':
                    bridge = 'other'
                elif style['Bridge'] == 'Saddle':
                    bridge = 'saddle'
                elif style['Bridge'] == 'Single bridge':
                    bridge = 'single_Bridge'
                elif style['Bridge'] == 'Unifit':
                    bridge = 'unifit'
                elif style['Bridge'] == 'Universal':
                    bridge = 'universal'
                hinge = ''
                if style['Hinge'] == 'Hingeless':
                    hinge = 'hingeless'
                elif style['Hinge'] == 'Micro spring Hinge':
                    hinge = 'micro_spring_hinge'
                elif style['Hinge'] == 'Regular Hinge':
                    hinge = 'regular_hinge'
                elif style['Hinge'] == 'Screwless Hinge':
                    hinge = 'screwless_hinge'
                elif style['Hinge'] == 'Spring Hinge':
                    hinge = 'spring_hinge'
                spec_lenses_type_id = self.env['spec.lenses.type'].search([('name', '=', style['LensType'])], limit=1)
                if not spec_lenses_type_id.id:
                    spec_lenses_type_id = self.env['spec.lenses.type'].create({
                        'name': style['LensType'],
                    })
                rx = ''
                if style['RX'] == 'Other':
                    rx = 'other'
                elif style['RX'] == 'Prescription available & Rx adaptable.':
                    rx = 'prescription_available_adaptable'
                elif style['RX'] == 'Prescription available.':
                    rx = 'prescription_adaptable'
                elif style['RX'] == 'Rx adaptable.':
                    rx = 'rx_daptable.'
                clip = ''
                if style['ClipOnOption'] == 'Available as a Sunglass.':
                    clip = 'available_sunglass.'
                elif style['ClipOnOption'] == 'Clip-on Available':
                    clip = 'clip_available'
                elif style['ClipOnOption'] == 'Clip-on included.':
                    clip = 'clip_included'
                elif style['ClipOnOption'] == 'Magnetic clip-on available':
                    clip = 'magnetic_clip_available'
                elif style['ClipOnOption'] == 'Magnetic clip-on included.':
                    clip = 'magnetic_clip_included'
                elif style['ClipOnOption'] == 'Other':
                    clip = 'other'
                side = ''
                if style['Sideshields'] == 'Detachable':
                    side = 'detachable'
                elif style['Sideshields'] == 'Flat fold':
                    side = 'flat_fold'
                elif style['Sideshields'] == 'Other':
                    side = 'other'
                elif style['Sideshields'] == 'Permanent':
                    side = 'permanent'
                warranty = ''
                if style['Warranty'] == '1-year warranty.':
                    warranty = '1_year_arranty'
                elif style['Warranty'] == '2-year warranty.':
                    warranty = '2_year_arranty'
                elif style['Warranty'] == '3-year warranty.':
                    warranty = '3_year_arranty'
                elif style['Warranty'] == 'Lifetime warranty on manufacturer’s defects':
                    warranty = 'lifetime_year_arranty'
                elif style['Warranty'] == 'Material defects or workmanship: 12 month warranty.':
                    warranty = '12_year_arranty'
                elif style['Warranty'] == 'Material defects or workmanship: 24 month warranty.':
                    warranty = '24_year_arranty'
                elif style['Warranty'] == 'Other':
                    warranty = 'other'
                elif style['Warranty'] == 'Unconditional lifetime warranty.':
                    warranty = 'unconditional_year_arranty'

                product_template_id = self.env['product.template'].search([('collection_id', '=', spec_collection_collection_id.id),
                                                                        ('frame_manufacturer_id', '=', spec_frame_manufacturer_id.id),
                                                                        ('brand_id', '=', spec_brand_brand_id.id),
                                                                        ('sfmid', '=', int(style['StyleFramesMasterID']))
                                                                        ], limit=1)
                if not product_template_id.id:
                    product_template_id = self.env['product.template'].with_context(disable_varients=True, create_product_product=False).create({
                        'type': 'product',
                        'material_frame_id': spec_frame_material_id.id,
                        'shap_id': spec_shape_shape_id.id,
                        'gender_ids': spec_gender_type_id.id,
                        'age': age if age != '' else None,
                        'frame_type_id': spec_frame_type_id.id,
                        'rim': rim if rim != '' else None,
                        'edge_type': edge if edge != '' else None,
                        'bridge_fix': bridge if bridge != '' else None,
                        'hinge': hinge if hinge != '' else None,
                        'lenses': spec_lenses_type_id.id,
                        'rx': rx if rx != '' else None,
                        'clip_on_option': clip if clip != '' else None,
                        'side_shields': side if side != '' else None,
                        'warranty': warranty if warranty != '' else None,
                        'is_sunclass': True if style['Sunglasses'] == 'Sunglasses' else False,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                        'discontinue': True if style['StyleStatus'] == 'D' else False,
                        'discont_date': fields.datetime.strptime(style['StyleDiscontinuedOn'],'%m/%d/%Y') if style['StyleStatus'] == 'D' else None,
                        'frames_data_last_sync': fields.datetime.now().date(),
                        'list_price': float(style['Retail']) if style['Retail'] else 0,
                        'wholesale_cost': float(style['Wholesale']) if style['Wholesale'] else 0,
                    })
                else:
                    product_template_id.update({
                        'material_frame_id': spec_frame_material_id.id,
                        'shap_id': spec_shape_shape_id.id,
                        'gender_ids': spec_gender_type_id.id,
                        'age': age if age != '' else None,
                        'frame_type_id': spec_frame_type_id.id,
                        'rim': rim if rim != '' else None,
                        'edge_type': edge if edge != '' else None,
                        'bridge_fix': bridge if bridge != '' else None,
                        'hinge': hinge if hinge != '' else None,
                        'lenses': spec_lenses_type_id.id,
                        'rx': rx if rx != '' else None,
                        'clip_on_option': clip if clip != '' else None,
                        'side_shields': side if side != '' else None,
                        'warranty': warranty if warranty != '' else None,
                        'is_sunclass': True if style['Sunglasses'] == 'Sunglasses' else False,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                        'discontinue': True if style['StyleStatus'] == 'D' else False,
                        'discont_date': fields.datetime.strptime(style['StyleDiscontinuedOn'],'%m/%d/%Y') if style['StyleStatus'] == 'D' else None,
                        'frames_data_last_sync': fields.datetime.now().date(),
                        'list_price': float(style['Retail']) if style['Retail'] else 0,
                        'wholesale_cost': float(style['Wholesale']) if style['Wholesale'] else 0,
                    })
                spec_color_family_id = self.env['spec.color.family'].search([('name', '=', configuration['Color'])], limit=1)
                if not spec_color_family_id.id:
                    spec_color_family_id = self.env['spec.color.family'].create({
                        'name': configuration['Color'],
                    })
                spec_color_code_family_id = self.env['spec.color.code.family'].search([('name', '=', configuration['ColorCode'])], limit=1)
                if not spec_color_code_family_id.id:
                    spec_color_code_family_id = self.env['spec.color.code.family'].create({
                        'name': configuration['ColorCode'],
                    })
                spec_lens_colors_id = self.env['spec.lens.colors'].search([('name', '=', configuration['LensColor'])], limit=1)
                if not spec_lens_colors_id.id:
                    spec_lens_colors_id = self.env['spec.lens.colors'].create({
                        'name': configuration['LensColor'],
                    })
                product_product_id = self.env['product.product'].search([('barcode', '=', configuration['UPC'])], limit=1)
                if product_product_id:
                    product_product_id.update({
                        'eye': configuration['Eye'],
                        'bridge': configuration['Bridge'],
                        'temple': configuration['Temple'],
                        'color_id': spec_color_family_id.id,
                        'color_code_id': spec_color_code_family_id.id,
                        'lens_color_id': spec_lens_colors_id.id,
                        'a': float(configuration['A']) if configuration['A'] else 0,
                        'b': float(configuration['B']) if configuration['B'] else 0,
                        'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                        'ed': float(configuration['ED']) if configuration['ED'] else 0,
                        'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                        'barcode': configuration['UPC'],
                        'default_code': configuration['SKU'],
                        # 'list_price': float(configuration['Retail']) if configuration['Retail'] else 0,
                        'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                        'list_price': float(style['Retail']) if style['Retail'] else float(configuration['SalePrice']),
                        'configurations_last_modified_on': fields.datetime.now().date(),
                    })
                else:
                    product_product_id = self.env['product.product'].with_context(disable_varients=True, create_product_product=False).create({
                        # 'name': spec_collection_collection_id.name + " " + style['StyleName'] + "(" + configuration['UPC'] + ")",
                        'eye': configuration['Eye'],
                        'bridge': configuration['Bridge'],
                        'temple': configuration['Temple'],
                        'color_id': spec_color_family_id.id,
                        'color_code_id': spec_color_code_family_id.id,
                        'lens_color_id': spec_lens_colors_id.id,
                        'a': float(configuration['A']) if configuration['A'] else 0,
                        'b': float(configuration['B']) if configuration['B'] else 0,
                        'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                        'ed': float(configuration['ED']) if configuration['ED'] else 0,
                        'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                        'barcode': configuration['UPC'],
                        'default_code': configuration['SKU'],
                        # 'list_price': float(configuration['Retail']) if configuration['Retail'] else 0,
                        'product_min_qty': float(configuration['Min_Qty']) if configuration['Min_Qty'] else 0,
                        'product_max_qty': float(configuration['Max_Qty']) if configuration['Max_Qty'] else 0,
                        'product_tmpl_id': product_template_id.id,
                        'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                        'list_price': configuration['SalePrice'],
                        'configurations_last_modified_on': fields.datetime.now().date(),
                    })
                    if style['Vendor'] and style['Vendor'] != '0':
                        product_supplierinfo = self.env['product.supplierinfo'].create({
                            'name': style['Vendor'],
                            # 'product_id': product_product_id.id,
                            'min_qty': 1,
                            'wholesale_cost': float(configuration['SalePrice']),
                            'price': float(configuration['SalePrice']),
                            'product_tmpl_id': product_template_id.id,
                        })
            return True
        except:
            return False

    def import_frames_by_cfmid(self, cfmids, vendor):
        styles_and_configurations = self.get_styles_and_configurations_by_cfmid(cfmids, vendor)
        return self.import_frames(styles_and_configurations, [], '')

    def sync_frames_by_cfmid(self, cfmids, vendor):
        styles_and_configurations = self.get_styles_and_configurations_by_cfmid(cfmids, 0)
        return self.sync_frames(styles_and_configurations, [])

    def sync_existing_frames_by_cfmid(self):
        cfmids = self.env['product.template'].search([('collection_id', 'in', self.env['spec.collection.collection'].search([]).ids)]).mapped('collection_id')
        styles_and_configurations = self.get_styles_and_configurations_by_cfmid(cfmids, 0)
        return self.sync_frames(styles_and_configurations, [])