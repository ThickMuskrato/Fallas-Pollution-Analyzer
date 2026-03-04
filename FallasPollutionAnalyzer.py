import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox


report_text = ""


def load_data(filename):
    data = []

    with open(filename, "r") as f:
        reader = csv.DictReader(f)

        date_col = None
        pm_col = None

        for col in reader.fieldnames:
            low = col.lower()
            if low in ["date", "fecha"]:
                date_col = col
            if "pm2.5" in low or "pm25" in low:
                pm_col = col

        if not date_col or not pm_col:
            return []

        for row in reader:
            try:
                date = datetime.strptime(row[date_col], "%Y-%m-%d")
            except:
                try:
                    date = datetime.strptime(row[date_col], "%d/%m/%Y")
                except:
                    continue

            try:
                pm = float(row[pm_col])
            except:
                continue

            data.append({"date": date, "pm25": pm})

    return data


def get_period(date):
    if date.month == 3 and 15 <= date.day <= 19:
        return "Fallas"
    return ""


def mean(values):
    if not values:
        return 0
    return sum(values) / len(values)


def run():
    global report_text

    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    data = load_data(file_path)

    if not data:
        messagebox.showerror("Error", "Could not load data") #Visual Error Message
        return

    for row in data:
        row["period"] = get_period(row["date"])

    fallas = []
    others = []

    for row in data:
        if row["period"] == "Fallas":
            fallas.append(row["pm25"])
        else:
            others.append(row["pm25"])

    if not fallas:
        messagebox.showinfo("Info", "No Fallas data found")
        return

    fallas_mean = mean(fallas)
    others_mean = mean(others)
    difference = fallas_mean - others_mean

    percent = 0
    if others_mean != 0:
        percent = (difference / others_mean) * 100

    WHO_LIMIT = 15
    fallas_bad = 0
    others_bad = 0

    for x in fallas:
        if x > WHO_LIMIT:
            fallas_bad += 1

    for x in others:
        if x > WHO_LIMIT:
            others_bad += 1

    data_sorted = []

    for row in data:
        data_sorted.append(row)

    n = len(data_sorted)

    for i in range(n):
        max_index = i
        for j in range(i + 1, n):
            if data_sorted[j]["pm25"] > data_sorted[max_index]["pm25"]:
                max_index = j
        temp = data_sorted[i]
        data_sorted[i] = data_sorted[max_index]
        data_sorted[max_index] = temp

    top10 = []
    count = 0
    for row in data_sorted:
        if count < 10:
            top10.append(row)
            count += 1

    report = ""
    report += "FALLAS PM2.5 AIR POLLUTION ANALYSIS\n\n"
    report += "Fallas entries: " + str(len(fallas)) + "\n"
    report += "Average PM2.5 during Fallas: " + str(round(fallas_mean, 2)) + "\n"
    report += "Average PM2.5 other days: " + str(round(others_mean, 2)) + "\n"
    report += "Difference: " + str(round(difference, 2)) + "\n"
    report += "Percent increase: " + str(round(percent, 2)) + "%\n\n"
    report += "WHO limit 15 µg/m³\n"
    report += "Fallas above limit: " + str(fallas_bad) + "/" + str(len(fallas)) + "\n"
    report += "Other above limit: " + str(others_bad) + "/" + str(len(others)) + "\n\n"
    report += "Top 10 Worst Days\n"

    index = 1
    for row in top10:
        report += str(index) + ". " + str(row["date"].date()) + " - " + str(round(row["pm25"], 2)) + " " + row["period"] + "\n"
        index += 1

    report_text = report

    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, report_text)


def save_report():
    global report_text

    if report_text == "":
        messagebox.showinfo("Info", "Run analysis first")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if save_path:
        with open(save_path, "w") as f:
            f.write(report_text)


root = tk.Tk()
root.title("Air Analysis")
root.geometry("550x450")

run_button = tk.Button(root, text="Select CSV and Run", command=run)
run_button.pack(pady=10)

save_button = tk.Button(root, text="Save Report", command=save_report)
save_button.pack(pady=5)

text_box = tk.Text(root, width=65, height=20)
text_box.pack(pady=10)

root.mainloop()