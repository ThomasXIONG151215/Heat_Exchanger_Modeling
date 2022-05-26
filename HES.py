from tabnanny import check
import streamlit as st
import math as mt
import CoolProp.CoolProp as prp
import matplotlib.pyplot as plt
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI

class HE_sim():
    def __init__(self):
        self.eps = 0 #换热效率
        self.Cmin = 0
        self.Cmax = 0
        self.c = 0 #Cmin/Cmax
        self.n = 0 #number of shells
        self.NTU = 0
        self.As = 0 
        self.U = 0# Overall heat transfert coefficient
        self.p = 101325 #Pa  
        self.T_mins = [273.154, 375.5, 90, 169.85, 251]
        self.T_maxs = [372, 1000, 1000, 248, 1000]
        self.Materials = ['Water', 'Steam', 'Air', 'R134a liquid', 'R134a gaz']
        self.Minibase = {}
        for i,j,k in zip(self.Materials, self.T_mins, self.T_maxs):
            self.Minibase[i] = (j, k)

    def Check_and_Update(self, mat_h, mat_c, T_h_entry, T_h_exit, T_c_entry, T_c_exit, pinch): #查验材料参数是否在准许范围内
        
        self.check_messages = []        
        T_h_in = T_h_entry
        T_c_in = T_c_entry

        H_h_in = prp.PropsSI("H", "T", T_h_in, "P", self.p, mat_h)
        H_c_in = prp.PropsSI("H", "T", T_c_in, "P", self.p, mat_c)
    
        H_h_out = prp.PropsSI("H" ,"T", T_c_in,"P", self.p, mat_c) 
        T_h_out = prp.PropsSI("T", "H", H_h_out, "P", self.p, mat_h)

        H_c_in = prp.PropsSI("H", "T", T_c_in, "P", self.p, mat_c)

        H_c_out = prp.PropsSI("H", "T", T_h_in, "P", self.p, mat_h)
        T_c_out = prp.PropsSI("T", "H", H_c_out, "P", self.p, mat_c)

        
        #constraint 1
        if T_h_entry < T_h_exit:
            self.check_messages.append("Hot Source Error")
        if T_c_entry > T_c_exit:
            self.check_messages.append("Cold Source Error")

        # constraint 2
        if H_h_in < H_c_in:
            self.check_messages.append("Enthalpy Unbalanced")

        # constraint 3
        if T_h_in - T_c_out < pinch:
            self.check_messages.append("Pinch unrespected")

        #如果没啥事儿
        if len(self.check_messages) == 0:
            print("Constraints Checked, No Problem")
            
            cp_h = (H_h_in - H_h_out) / (T_h_in - T_h_out) # J/(kg.C)
            
            cp_c = (H_c_in - H_c_out) / (T_c_in - T_c_out)
            
            m_dot_h = 2

            m_dot_c = 2 #kg/s
            #Q_dot = m_dot_c * cp_c * (T_c_out - T_c_in)
            #Q_dot_max = min(m_dot_c * cp_c, m_dot_h * cp_h) * (T_h_in - T_c_in)

            Q_max = (prp.PropsSI("H", "T", T_h_in, "P", self.p, mat_c) - prp.PropsSI("H", "T", T_c_in, "P", self.p, mat_c)) #理论最大换热焓变

            self.Cmin = min(m_dot_c * cp_c, m_dot_h * cp_h)
            self.Cmax = max(m_dot_c * cp_c, m_dot_h * cp_h)
            self.c = self.Cmin / self.Cmax
            self.eps =  (H_c_out - H_c_in) / Q_max
            
            print("Parameters Updated")

        elif len(self.check_messages) >= 1:
            for mes in self.check_messages: 
                print(mes)

    def NTU_and_As(self, option, U):
        self.U = U
        NTU = 0
        if option == 'Double_pipe / Parallel-flow': 
            NTU = - mt.log10(1 - self.eps * (1 + self.c))/(1 + self.c)
        elif option == 'Double_pipe / Counter-flow' and self.c < 1: 
            NTU = 1/(self.c - 1) * mt.log10((self.eps - 1) / (self.eps * self.c - 1))
        elif option == 'Double_pipe / Counter-flow' and self.c == 1: 
            NTU = self.eps / (1 - self.eps)
        elif option == 'Shell and tube / One-shell pass': 
            NTU = - 1/(mt.sqrt(1 + self.c**2)) * mt.log10((2/self.eps - 1 - self.c - mt.sqrt(1 + self.c**2))/(2/self.eps - 1 - self.c + mt.sqrt(1 + self.c**2)))
        #'Shell and tube / n-shell pass', 
        elif option == 'Cross-flow / Cmax mixed, Cmin unmixed':
            NTU = - mt.log10(1 + mt.log10(1 - self.eps * self.c)/self.c)
        elif option == 'Cross-flow / Cmax unmixed, Cmin mixed':
            NTU = - mt.log10(self.c * mt.log10(1 - self.eps) + 1) / self.c
        elif option == 'Others':
            NTU = - mt.log10(1 - self.eps)

        self.NTU = NTU

        self.As = NTU * self.Cmin / self.U

        


def app():
    st.title('HEO module')
    st.write('Optimizing the heat exchange efficiency')
    HE = HE_sim()
    OPTIONS = ['Double_pipe / Parallel-flow', 'Double_pipe / Counter-flow', 'Shell and tube / One-shell pass', 'Shell and tube / n-shell pass', 'Cross-flow / Cmax mixed, Cmin unmixed', 'Cross-flow / Cmax unmixed, Cmin mixed', 'Others']

    selection = st.selectbox("Choose option", OPTIONS)

    if selection == 'Shell and tube / One-shell pass': number_of_passes = st.number_input("Number of passes:")

    U = st.number_input("Overall heat transfer coefficient U:")
    
    source_materials = ['Water', 'Air', 'Steam', 'R134a liquid', 'R134a gaz']

    with st.expander("Hot Source Settings"):
        mat_hot = st.selectbox("Hot Source", source_materials)
        T_h_min, T_h_max = HE.Minibase[mat_hot]
        T_h_max = float(T_h_max)
        T_h_min = float(T_h_min)
        T_h_entry = st.slider("Hot Source Entry Temperature", value = (T_h_max + T_h_min) / 2 , max_value = T_h_max, min_value = T_h_min)
        T_h_exit = st.slider("Hot Source Exit Temperature", value = (T_h_entry + T_h_min) / 2,max_value = T_h_entry, min_value = T_h_min)

    with st.expander("Cold Source Settings"):
        mat_cold = st.selectbox("Cold Source", source_materials)
        T_c_min, T_c_max = HE.Minibase[mat_cold]
        T_c_max = float(T_c_max)
        T_c_min = float(T_c_min)
        T_c_entry = st.slider("Cold Source Entry Temperature",value = (T_c_max + T_c_min) / 2 , max_value = T_c_max, min_value = T_c_min)
        T_c_exit = st.slider("Cold Source Exit Temperature", value = (T_c_max + T_c_entry) / 2 ,max_value = T_c_max, min_value = T_c_entry)

 
    pinch = st.number_input("Pinch ")
       
    coolProp_translate = {'Steam': 'Water', 'Water': 'Water', 'Air': 'Air', 'R134a liquid': 'R134a', 'R134a gaz': 'R134a'}

    mat_cold = coolProp_translate[mat_cold]
    mat_hot = coolProp_translate[mat_hot]

    HE.Check_and_Update(mat_hot, mat_cold, T_h_entry, T_h_exit, T_c_entry, T_c_exit, pinch)
    
    st.write('Settings Check Report',HE.check_messages)

    HE.NTU_and_As(selection, U)

    col1, col2 = st.columns(2)

    st.metric(label = "Surface", value = str(HE.As) + "m2")
    #st.metric(label = "Surface", value = str(HE.As) + "m2", delta = "1.1 m2")
