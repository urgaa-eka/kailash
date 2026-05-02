import React, { useState } from 'react';
import { usePricingTable } from '../hooks/useApi';
import { Car, TrendingUp, DollarSign, BarChart2, Loader2 } from 'lucide-react';

const vehicleTypes = ['sedan', 'suv', 'hatchback', 'motorcycle', 'truck', 'bus'];

const AutomobilePricing = () => {
  const [selectedVehicle, setSelectedVehicle] = useState('sedan');
  const { data, isLoading, error } = usePricingTable(selectedVehicle);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2" style={{ color: '#0A3D62' }}>
            <Car className="w-8 h-8" />
            Automobile Pricing Engine
          </h1>
          <p className="text-gray-600 mt-2">Uniform pricing based on Market + GST Software data fusion</p>
        </div>
        <div className="flex items-center gap-2" style={{ color: '#FFC312' }}>
          <BarChart2 className="w-6 h-6" />
          <span className="font-semibold">Go4Garage URGAA</span>
        </div>
      </div>

      {/* Vehicle Type Selector */}
      <div className="flex gap-2 flex-wrap">
        {vehicleTypes.map(type => (
          <button
            key={type}
            onClick={() => setSelectedVehicle(type)}
            className={`px-6 py-3 rounded-lg capitalize font-medium transition-all ${
              selectedVehicle === type 
                ? 'text-white shadow-lg' 
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
            }`}
            style={selectedVehicle === type ? { background: '#0A3D62' } : {}}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Pricing Table */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="w-12 h-12 animate-spin mb-4" style={{ color: '#0A3D62' }} />
          <p className="text-gray-600">Loading pricing data...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 font-medium">Error loading pricing data</p>
          <p className="text-red-600 text-sm mt-2">{error.message}</p>
        </div>
      ) : data?.pricing?.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">No pricing data available for {selectedVehicle}</p>
          <p className="text-yellow-600 text-sm mt-2">Add sample data to get started</p>
        </div>
      ) : (
        <div className="grid gap-4">
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">Total Services:</span>
              <span className="font-bold" style={{ color: '#0A3D62' }}>{data?.services || 0}</span>
            </div>
          </div>
          
          {data?.pricing?.map((item, idx) => (
            <div 
              key={idx} 
              className="bg-white rounded-xl border-2 p-6 hover:shadow-lg transition-all"
              style={{ borderColor: '#0A3D62' }}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg capitalize" style={{ color: '#0A3D62' }}>
                    {item.service_type.replace(/_/g, ' ')}
                  </h3>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      <BarChart2 className="w-4 h-4" />
                      {item.sample_size} data points
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      Market + GST fusion
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold" style={{ color: '#FFC312' }}>
                    ₹{item.uniform_price?.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Range: ₹{item.min_price} - ₹{item.max_price}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Avg: ₹{item.avg_price}
                  </p>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t flex gap-4 text-xs text-gray-500">
                <span>Market data: {item.sources?.market_data || 0}</span>
                <span>GST software: {item.sources?.gst_software || 0}</span>
                <span>Region: {item.region}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AutomobilePricing;