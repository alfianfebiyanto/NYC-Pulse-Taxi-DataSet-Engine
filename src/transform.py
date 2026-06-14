import pandas as pd

class DataTransformer:
    
    @staticmethod
    # Rename Coloumns
    def rename_columns_trip(df):
        return df.rename(columns={
            "VendorID": "vendor_id",
            "RatecodeID": "rate_code_id",
            "tpep_pickup_datetime": "pickup_datetime",
            "tpep_dropoff_datetime": "dropoff_datetime",
            "PULocationID": "pu_location_id",
            "DOLocationID": "do_location_id",
            "Airport_fee": "airport_fee"
        })

    @staticmethod
    # Add Datetime
    def enrich_datetime(df):
        df['pickup_hour'] = df['pickup_datetime'].dt.hour
        df['pickup_date'] = df['pickup_datetime'].dt.date
        df['pickup_day_name'] = df['pickup_datetime'].dt.day_name()
        df['trip_duration_minutes'] = ((df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60).round(1)
        df['is_weekend'] = df['pickup_datetime'].dt.weekday >= 5
        return df

    @staticmethod
    # Add Time Period
    def add_time_period(df):
        def _period(hour):
            if 7 <= hour <= 9: return 'Morning Rush'
            if 0 <= hour <= 5: return 'Late Night'
            if 6 <= hour <= 10: return 'Morning'
            if 11 <= hour <= 15: return 'Afternoon'
            if 16 <= hour <= 19: return 'Evening Rush'
            if 20 <= hour <= 23: return 'Night'
            return 'Invalid'
        df['time_period'] = df['pickup_hour'].apply(_period)
        return df

    @staticmethod
    # Add Mapping Categorical Payment and Store and fwd flag
    def map_categorical(df):
        
        # Payment Mapping
        payment_map = {
            1: 'Credit Card', 
            2: 'Cash', 
            3: 'No Charge',
            4: 'Dispute',
            0: 'Unknown'}

        # Impleme
        df['payment_type'] = df['payment_type'].map(payment_map).fillna('Invalid')

        # Store Mapping
        store_map = {
            'Y': 'Store and Forward', 
            'N': 'Normal'}

        df['store_and_fwd_flag'] = df['store_and_fwd_flag'].map(store_map).fillna('Invalid')
        return df

    @staticmethod
    def join_zones(df, zone_df):
        # Pickup Location
        df = df.merge(
            zone_df[['location_id', 'zone', 'borough', 'service_zone']],
            left_on='pu_location_id', right_on='location_id', how='left'
        )
        df.rename(columns={'zone': 'pu_zone', 'borough': 'pu_borough', 'service_zone': 'pu_service_zone'}, inplace=True)
        df.drop(columns=['location_id'], inplace=True)
        
        # Dropoff Location
        df = df.merge(
            zone_df[['location_id', 'zone', 'borough', 'service_zone']],
            left_on='do_location_id', right_on='location_id', how='left'
        )
        df.rename(columns={'zone': 'do_zone', 'borough': 'do_borough', 'service_zone': 'do_service_zone'}, inplace=True)
        df.drop(columns=['location_id'], inplace=True)
        return df


    @staticmethod
    def reorder_columns(df):
        final_order = [
            'vendor_id', 'pickup_datetime', 'dropoff_datetime', 'trip_duration_minutes',
            'pickup_date', 'pickup_hour', 'pickup_day_name', 'is_weekend', 'time_period',
            'passenger_count', 'trip_distance', 'rate_code_id', 'store_and_fwd_flag',
            'pu_location_id', 'pu_zone', 'pu_borough', 'pu_service_zone',
            'do_location_id', 'do_zone', 'do_borough', 'do_service_zone',
            'payment_type', 'fare_amount', 'extra', 'mta_tax', 'tip_amount',
            'tolls_amount', 'improvement_surcharge', 'congestion_surcharge',
            'airport_fee', 'cbd_congestion_fee', 'total_amount'
        ]
        available = [c for c in final_order if c in df.columns]
        return df[available]


