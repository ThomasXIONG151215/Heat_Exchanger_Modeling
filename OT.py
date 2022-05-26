from turtle import hideturtle
import streamlit as st

#assume the tube is composed by limestone of heat coefficient 2.9 W/m.K
# we need its thickness in mm in order to calculate the wall resistance


# references to obtain the fouling resistance
#Source: http://www.hcheattransfer.com/fouling_factors2.html
# https://www.unitsconverters.com/en/Btu(It)/Hmft2mdegf-To-W/(M2k)/Utu-4404-4398?MeasurementId=66&From=4404&To=4398&UtoU=true
#324.82/  Water : City or Well water
#Refrigerant Vapors (oil bearing)
#Compressed air

#def btu_to_w(btu):
  #  return 1/(1/btu * 5.678263)
# btu_to_w(0.001),btu_to_w(0.002),btu_to_w(0.0005)
# (0.000176110194261872, 0.000352220388523744, 8.8055097130936e-05)
R_f = {'Steam': 8.8055097130936 * 10 ** (-5), 'R134a liquid': 0.000176110194261872, 'R134a gaz': 0.000352220388523744, 'Water': 0.000252220194261872, 'Air': 0.000176110194261872}


#https://www.sciencedirect.com/topics/engineering/convection-heat-transfer-coefficient
#https://www.engineersedge.com/heat_transfer/convective_heat_transfer_coefficients__13378.htm
#forced convection
#假设空气与气态制冷剂的对流换热系数取同样范围
#假设所有液态材料取同样的对流换热系数范围
#假设蒸汽取condensing water vapor的对流换热系数范围
conv_h = {'Water': (10, 15000), 'Steam': (5000, 100000), 'R134a liquid': (100, 15000), 'R134a gaz': (10, 500), 'Air': (10, 500)}

# 管道材质k stainless stell k = 15 W/mK
#https://www.researchgate.net/post/Heat_Exchanger_Stainless_Steel_and_SA-106B_heat_transfer_coefficient_query#:~:text=Difference%20in%20material%20only%20affects%20the%20thermal%20conductivity.,change.%20Stainless%20Steel%3A%20thermal%20conductivity%20is%2015%20W%2FmK

#假设Rwall约等于0，同时Ai约等于A0，因此Ui约等于Uo

#p = 101325 #Pa
#k = 15 #W/mk

#Rwall = mt.log10(D_o / D_i) / (2 * mt.pi * k * L)


import CoolProp.CoolProp as prp
import math as mt


def app():
    st.title('OT module')
    st.write('Calculate the output temperature / overall transfer coefficient')

    fluid_i = st.selectbox('Cold Fluid', list(conv_h.keys()))
    h_i = conv_h[fluid_i]
    st.write('conv_h range', h_i)

    fluid_o = st.selectbox('Hot Fluid', list(conv_h.keys()))
    h_o = conv_h[fluid_o]
    st.write('conv_h range', h_o)

    L = st.number_input('Tube Length (mm)')

    D_i = st.number_input('Inside Diameter (mm)')
    D_o = st.number_input('Outside Diameter (mm)', min_value = D_i)

    Rfluid_i = R_f[fluid_i]
    Rfluid_o = R_f[fluid_o]

    h_i = conv_h[fluid_i]
    h_o = conv_h[fluid_o]

    U_min = 1 / (1/h_i[0] + 1/h_o[0] + Rfluid_i + Rfluid_o)

    U_max = 1 / (1/h_i[1] + 1/h_o[1] + Rfluid_i + Rfluid_o)

    st.write('Overall heat transfer coefficient range', (U_min, U_max))




