import pandas as pd
import streamlit as st
from datetime import datetime
import os

# ضبط عنوان الصفحة والتصميم
st.set_page_config(page_title="البرنامج المحاسبي البسيط", layout="wide", page_icon="📊")

# ملفات حفظ البيانات
TRANSACTIONS_FILE = "transactions.csv"
INVENTORY_FILE = "inventory.csv"

# تهيئة الملفات إذا لم تكن موجودة
if not os.path.exists(TRANSACTIONS_FILE):
    df_trans = pd.DataFrame(columns=["التاريخ", "النوع", "البيان / الوصف", "المبلغ", "العميل / المورد"])
    df_trans.to_csv(TRANSACTIONS_FILE, index=False)

if not os.path.exists(INVENTORY_FILE):
    df_inv = pd.DataFrame(columns=["اسم المنتج", "الكمية المتاحة", "سعر الشراء", "سعر البيع"])
    df_inv.to_csv(INVENTORY_FILE, index=False)

# دالة قراءة البيانات
def load_data(file_path):
    return pd.read_csv(file_path)

# دالة حفظ البيانات
def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# الواجهة الرئيسية
st.title("📊 البرنامج المحاسبي البسيط")
st.markdown("---")

# القائمة الجانبية
menu = ["الرئيسية والملخص", "تسجيل حركة جديدة", "إدارة المخزن", "سجل وتعديل الحركات"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

# 1. الصفحة الرئيسية والملخص
if choice == "الرئيسية والملخص":
    st.header("📈 ملخص الخزينة والحسابات")
    df_trans = load_data(TRANSACTIONS_FILE)
    
    if not df_trans.empty:
        total_income = df_trans[df_trans["النوع"] == "مبيعات (إيراد)"]["المبلغ"].sum()
        total_expenses = df_trans[df_trans["النوع"].isin(["مشتريات", "مصروفات"])]["المبلغ"].sum()
        net_balance = total_income - total_expenses

        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الإيرادات (المبيعات)", f"{total_income:,.2f} ج.م")
        col2.metric("إجمالي المصروفات والمشتريات", f"{total_expenses:,.2f} ج.م")
        col3.metric("صافي الخزينة الحالية", f"{net_balance:,.2f} ج.م")
        
        st.subheader("آخر الحركات المسجلة")
        st.dataframe(df_trans.tail(10), use_container_width=True)
    else:
        st.info("لا توجد حركات مسجلة حتى الآن. يمكنك إضافة حركة جديدة من القائمة الجانبية.")

# 2. تسجيل حركة جديدة
elif choice == "تسجيل حركة جديدة":
    st.header("📝 إضافة حركة مالية جديدة")
    
    with st.form("transaction_form"):
        trans_type = st.selectbox("نوع الحركة", ["مبيعات (إيراد)", "مشتريات", "مصروفات"])
        description = st.text_input("البيان / الوصف (مثلاً: فاتورة بيع / إيجار / بضاعة)")
        amount = st.number_input("المبلغ (ج.م)", min_value=0.0, format="%.2f")
        party = st.text_input("اسم العميل / المورد (اختياري)")
        date_selected = st.date_input("التاريخ", datetime.now())
        
        submit = st.form_submit_button("حفظ الحركة")
        
        if submit:
            if amount > 0 and description:
                df_trans = load_data(TRANSACTIONS_FILE)
                new_row = {
                    "التاريخ": str(date_selected),
                    "النوع": trans_type,
                    "البيان / الوصف": description,
                    "المبلغ": amount,
                    "العميل / المورد": party
                }
                df_trans = pd.concat([df_trans, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_trans, TRANSACTIONS_FILE)
                st.success("تم تسجيل الحركة بنجاح!")
            else:
                st.error("يرجى إدخال المبلغ والبيان بشكل صحيح.")

# 3. إدارة المخزن
elif choice == "إدارة المخزن":
    st.header("📦 إدارة المنتجات والمخزون")
    
    df_inv = load_data(INVENTORY_FILE)
    
    tab1, tab2 = st.tabs(["قائمة المنتجات", "إضافة منتج جديد"])
    
    with tab1:
        st.dataframe(df_inv, use_container_width=True)
        
    with tab2:
        with st.form("inventory_form"):
            item_name = st.text_input("اسم المنتج")
            qty = st.number_input("الكمية", min_value=0, step=1)
            buy_price = st.number_input("سعر الشراء (للقطعة)", min_value=0.0, format="%.2f")
            sell_price = st.number_input("سعر البيع (للقطعة)", min_value=0.0, format="%.2f")
            
            add_item = st.form_submit_button("إضافة المنتج")
            
            if add_item:
                if item_name:
                    new_item = {
                        "اسم المنتج": item_name,
                        "الكمية المتاحة": qty,
                        "سعر الشراء": buy_price,
                        "سعر البيع": sell_price
                    }
                    df_inv = pd.concat([df_inv, pd.DataFrame([new_item])], ignore_index=True)
                    save_data(df_inv, INVENTORY_FILE)
                    st.success(f"تم إضافة {item_name} إلى المخزن!")
                else:
                    st.error("يرجى إدخال اسم المنتج.")

# 4. سجل وتعديل الحركات
elif choice == "سجل وتعديل الحركات":
    st.header("📜 جميع الحركات المالية (تعديل / حذف)")
    df_trans = load_data(TRANSACTIONS_FILE)
    
    if not df_trans.empty:
        st.dataframe(df_trans, use_container_width=True)
        
        st.markdown("---")
        st.subheader("✏️ تعديل حركة مسجلة")
        
        # اختيار الحركة
        row_to_edit = st.selectbox("اختر رقم الحركة المراد تعديلها:", df_trans.index)
        
        current_row = df_trans.loc[row_to_edit]
        
        with st.form("edit_form"):
            # تحديد نوع الحركة الحالي
            types_list = ["مبيعات (إيراد)", "مشتريات", "مصروفات"]
            default_type_idx = types_list.index(current_row["النوع"]) if current_row["النوع"] in types_list else 0
            
            new_type = st.selectbox("نوع الحركة", types_list, index=default_type_idx)
            new_desc = st.text_input("البيان / الوصف", value=str(current_row["البيان / الوصف"]))
            new_amount = st.number_input("المبلغ (ج.م)", min_value=0.0, value=float(current_row["المبلغ"]), format="%.2f")
            new_party = st.text_input("اسم العميل / المورد", value=str(current_row["العميل / المورد"]) if pd.notna(current_row["العميل / المورد"]) else "")
            
            col_save, col_del = st.columns(2)
            submit_edit = st.form_submit_button("💾 حفظ التعديلات")
            
        if submit_edit:
            df_trans.loc[row_to_edit, "النوع"] = new_type
            df_trans.loc[row_to_edit, "البيان / الوصف"] = new_desc
            df_trans.loc[row_to_edit, "المبلغ"] = new_amount
            df_trans.loc[row_to_edit, "العميل / المورد"] = new_party
            save_data(df_trans, TRANSACTIONS_FILE)
            st.success("تم تعديل الحركة بنجاح!")
            st.rerun()

        st.markdown("---")
        if st.button("🗑️️ حذف هذه الحركة بالكامل"):
            df_trans = df_trans.drop(row_to_edit).reset_index(drop=True)
            save_data(df_trans, TRANSACTIONS_FILE)
            st.success("تم حذف الحركة بنجاح!")
            st.rerun()

        st.markdown("---")
        csv_data = df_trans.to_csv(index=False).encode('utf-8-sig')
        st.download_button("تنزيل التقرير كملف Excel (CSV)", csv_data, "report.csv", "text/csv")
    else:
        st.info("لا توجد حركات مسجلة حالياً.")
