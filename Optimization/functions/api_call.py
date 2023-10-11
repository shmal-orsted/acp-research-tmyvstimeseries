import requests
import json
import pandas as pd
import requests_cache


def api_call_func(api_key, api_url, src_args, weather_df, gcr, acdc, year, ac):
    """
    Modular function to call the api
    :param api_key: environment variable accessed with os.environ["API_KEY"]
    :param api_url: url for api call for the functions you're trying to do, basic is the manual url
    :param src_args: json formatted params for the run you're completing
    :return: data_json: data returned from the api call
    :return: return code: an api return code, 200 successful, anything else is usually an error for some reason or another
    """

    outputs_dict = {}
    outputs_list = []

    # Change the src_args values to the current range value
    src_args["DCCapacity"] = src_args["ACCapacity"] * acdc
    src_args["GCR"] = gcr/100
    src_args["ACCapacity"] = ac

    x = src_args["DCCapacity"]
    y = src_args["GCR"]

    # adjusting df call to just take required columns
    weather_df = weather_df[["GHI", "DHI", "Tamb", "Wspd"]]

    #TODO add functionality to choose dat or csv file for api call

    #temp adding caching for testing
    session = requests_cache.CachedSession('testing_cache')

    src_energy_manual_request = session.post(
        url=api_url,
        params=src_args,
        verify=False,
        headers={'X-ApiKey': api_key}
        # , files={'DatFile': open(DatFile_filename, 'rb')}
        , data={'Json8760': json.dumps({n: weather_df[n].to_list() for n in weather_df})}
    )

    # src_energy_manual_request = requests.post(
    #     url=api_url,
    #     params=src_args,
    #     verify=False,
    #     headers={'X-ApiKey': api_key}
    #     # , files={'DatFile': open(DatFile_filename, 'rb')}
    #     , data={'Json8760': json.dumps({n: weather_df[n].to_list() for n in weather_df})}
    # )

    if (src_energy_manual_request.status_code >= 400):
        print(f"API request failed. Error status code: {src_energy_manual_request.status_code}\n" +
              f"Reason: {src_energy_manual_request.reason}\n" + f"Message: {src_energy_manual_request.text}")
        raise Exception(f"API request failed. Error status code: {src_energy_manual_request.status_code}\n" +
                        f"Reason: {src_energy_manual_request.reason}\n" + f"Message: {src_energy_manual_request.text}")

    if (src_energy_manual_request.status_code == 200):
        json_dict = src_energy_manual_request.json()

        # convert SystemAttributes to dataframe
        SystemAttributes = json_dict['SystemAttributes']
        df_SystemAttributes = pd.DataFrame.from_dict(SystemAttributes, orient='index',
                                                     columns=['Value']).reset_index().rename(
            columns={'index': 'Attribute'})
        pd.options.display.float_format = '{:,.3f}'.format

        # convert Metadata to dataframe
        Metadata = json_dict['Metadata']
        df_Metadata = pd.DataFrame.from_dict(Metadata, orient='index', columns=['Value']).reset_index().rename(
            columns={'index': 'Attribute'})
        pd.options.display.float_format = '{:,.3f}'.format

        # convert SummaryAnnual to dataframe
        SummaryAnnual = json_dict['SummaryAnnual']
        df_SummaryAnnual = pd.DataFrame.from_dict(SummaryAnnual, orient='index',
                                                  columns=['Value']).reset_index().rename(
            columns={'index': 'Attribute'})
        pd.options.display.float_format = '{:,.2f}'.format

        # convert SummaryMonthly to dataframe
        SummaryMonthly = json_dict['SummaryMonthly']
        df_SummaryMonthly = pd.DataFrame.from_dict(SummaryMonthly, orient='columns')
        pd.options.display.float_format = '{:,.2f}'.format

        # show annual summary computed from monthly data
        pd.options.display.float_format = '{:,.0f}'.format
        # print(df_SummaryMonthly[['GlobHor', 'GlobInc', 'E_Grid']].sum().to_frame())

        # convert Hourly to dataframe
        Hourly = json_dict['Hourly']
        df_Hourly = pd.DataFrame.from_dict(Hourly, orient='index')
        pd.options.display.float_format = '{:,.0f}'.format

        # calculate common metrics - total energy, specific yield and performance ratio

        api_energy = df_Hourly['E_Grid'].sum() / 1000
        api_yield = api_energy / src_args['DCCapacity']
        api_pr = api_yield / (df_Hourly['GlobInc'].sum() / 1000)

        # print('API energy generation (kWh): ' + '{:,.0f}'.format(api_energy))
        # print('API specific yield (kWh/kWp/yr): ' + '{:.0f}'.format(api_yield))
        # print('API performance ratio (%): ' + '{:.1%}'.format(api_pr))

        # negative values mean the API predicted values LOWER than the comparison
        # positive values mean the API predicted values HIGHER than the comparison

        # delta_energy = (api_energy / comparison_energy) - 1
        # delta_yield = (api_yield / comparison_yield) - 1
        # delta_pr = (api_pr - comparison_pr)
        # print('API energy generation relative to comparison: ' + '{:.1%}'.format(delta_energy))
        # print('API specific yield relative to comparison: ' + '{:.1%}'.format(delta_yield))
        # print('API performance ratio relative to comparison: ' + '{:.1%}'.format(delta_pr))

        # convert Metadata to dataframe
        LossTreeAnnual = json_dict['LossTreeAnnual']
        df_losstree = pd.DataFrame.from_dict(LossTreeAnnual, orient='index', columns=['Value'])
        pd.options.display.float_format = '{:,.2%}'.format

        # this dictionary exposes the current rate limit settings and your organization's remaining balance
        # quota refers to your organization's annual contracted API call volume
        # remaining indicates the number of calls remaining under your subscription

        # convert api_metadata to dataframe
        api_metadata = json_dict['APIMetadata']
        df_api_metadata = pd.DataFrame.from_dict(api_metadata, orient='index')
        pd.options.display.float_format = '{:,.0f}'.format

        # calculate the NCF
        json_dict["NCF"] = (json_dict['SummaryAnnual']['netEnergy'] / (src_args["ACCapacity"] * 8760))

        # calculate AC/DC ratio and add to json dict
        json_dict["DC/AC Ratio"] = (y / src_args["ACCapacity"])

        # Add this run's results to the outputs dict
        outputs_dict[f"{year}"] = json_dict
        outputs_list.append(json_dict)

    return json_dict, src_energy_manual_request
    # json_dict = {}  # Placeholder for json-formatted response if successful


    # return src_energy_manual_request.json()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    api_call_func()