"""Desktop interface for SpoolProof. No web server or network access."""
import json, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from spoolproof import quote

class App:
    def __init__(self, root):
        self.root=root;root.title('SpoolProof | Before the first layer');root.geometry('1020x760')
        style=ttk.Style();style.theme_use('clam');style.configure('TLabel',font=('Segoe UI',11));style.configure('TButton',padding=8)
        shell=ttk.Frame(root,padding=20);shell.pack(fill='both',expand=True)
        ttk.Label(shell,text='SpoolProof',font=('Segoe UI',26,'bold')).pack(anchor='w')
        ttk.Label(shell,text='Know your costs. Check your stock. Keep your data offline.').pack(anchor='w',pady=(0,15))
        cols=ttk.Frame(shell);cols.pack(fill='both',expand=True)
        form=ttk.Frame(cols);form.pack(side='left',fill='y',padx=(0,20))
        self.vars={};self.last=None
        fields=[('grams','Filament per attempt (g)',60),('hours','Print time per attempt (hours)',3),('quantity','Finished parts',4),('filament_per_kg','Filament cost per kg',20),('watts','Average printer power (W)',100),('electricity_per_kwh','Electricity cost per kWh',.15),('machine_per_hour','Machine cost per hour',.5),('failure_probability','Failure probability (0–0.99)',.1),('labor_minutes','Labor per finished part (minutes)',10),('labor_per_hour','Labor cost per hour',12),('setup_cost','Setup cost for whole job',2),('margin','Target gross margin (0–0.99)',.3),('spool_remaining_g','Spool remaining (g)',300)]
        for row,(key,label,value) in enumerate(fields):
            ttk.Label(form,text=label).grid(row=row,column=0,sticky='w',pady=3)
            var=tk.StringVar(value=str(value));self.vars[key]=var
            ttk.Entry(form,textvariable=var,width=12).grid(row=row,column=1,padx=10)
        for row,(key,value) in enumerate(zip(('x','y','z'),(80,45,30)),len(fields)):
            ttk.Label(form,text=f'Part {key.upper()} (mm)').grid(row=row,column=0,sticky='w',pady=3)
            var=tk.StringVar(value=str(value));self.vars[key]=var
            ttk.Entry(form,textvariable=var,width=12).grid(row=row,column=1,padx=10)
        actions=ttk.Frame(form);actions.grid(row=17,column=0,columnspan=2,pady=12)
        ttk.Button(actions,text='Calculate',command=self.calculate).pack(side='left')
        ttk.Button(actions,text='Save report',command=self.save).pack(side='left',padx=8)
        self.output=tk.Text(cols,wrap='word',font=('Consolas',12),background='#111c2b',foreground='#e6f4f0',padx=18,pady=18)
        self.output.pack(side='left',fill='both',expand=True)
        ttk.Label(shell,text='Estimate only • Default envelope 245 × 245 × 245 mm • Currency follows your rates').pack(anchor='w',pady=(12,0))
        self.calculate()
    def calculate(self):
        try:
            j={k:v.get() for k,v in self.vars.items() if k not in ('x','y','z')}
            j['dimensions_mm']=[self.vars[k].get() for k in ('x','y','z')]
            r=quote(j);self.last=r
            msg=f"EXPECTED JOB COST   {r['expected_job_cost']:.2f}\nSUGGESTED PRICE     {r['suggested_price']:.2f}\n\nExpected filament: {r['expected_filament_g']:.2f} g\nStock: {'EXPECTED SUFFICIENT' if r['spool_expected_sufficient'] else 'SHORTAGE EXPECTED'}\nEnvelope: {'FITS AXIS-ALIGNED' if r['fits_axis_aligned'] else 'DOES NOT FIT AXIS-ALIGNED'}\n\n"
            msg+='\n\n'.join(r['limitations'])
            self.output.config(state='normal');self.output.delete('1.0','end');self.output.insert('1.0',msg);self.output.config(state='disabled')
        except (ValueError,KeyError,TypeError) as exc:
            self.last=None;messagebox.showerror('Check your inputs',str(exc))
    def save(self):
        self.calculate()
        if self.last is None:return
        p=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON report','*.json')])
        if p:
            try:
                with open(p,'w') as f:json.dump(self.last,f,indent=2)
            except OSError as exc:messagebox.showerror('Could not save',str(exc))
if __name__=='__main__':
    root=tk.Tk();App(root);root.mainloop()
