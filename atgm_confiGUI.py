import hexcompute as hc
import string
import serial as sl
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext as sct
import os
import atgmComms as AC
from tkinter import messagebox as msg

class Atgm_Diagnostic_GUI(object):
    
    def __init__(self):
        # declare a window
        self.root = tk.Tk()
        self.root.title("Serial Diagnostics")
        self.width = 600
        self.height = 200

        # if GUI is being run on a macOSX
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':
            s = ttk.Style()
            s.configure('TNotebook.Tab', padding=(12, 8, 12, 0))

	# declare 3 different tabs and name them
        # tab for serial comms
        self.tabcontrol = ttk.Notebook(self.root)
        self.serialportTab = ttk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.serialportTab, text='Serial Comms')
        # tab for basic commands
        self.atgmBasicCommandsTab = ttk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.atgmBasicCommandsTab, text='ATGM Commands')
        # tab for Configuration
        self.atgmconfigTab = ttk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.atgmconfigTab, text='ATGM Configuration')

        self.tabcontrol.pack(expand=1, fill='both')

        # Serial Port Tab

        # declare a holder frame
        self.frame = ttk.LabelFrame(self.serialportTab, text='Configure:', width=self.width, height=self.height)
        self.frame.grid(row=0, column=0)

        # declare a text entry to take the port
        # try and auto populate this 
        self.device_text = tk.StringVar()
        self.device_combobox = ttk.Combobox(self.frame, width=12, textvariable=self.device_text, state='readonly')
        self.device_combobox['values'] = self.__populateDeviceCombobox__()
        self.device_combobox.grid(row=1, column=0)
        self.device_label = ttk.Label(self.frame, text='Select port:')
        self.device_label.grid(row=0, column=0)
        # self.device_text= tk.StringVar()
        # self.textbox = ttk.Entry(self.frame, textvariable=self.device_text)
        # self.textbox.grid(row=0, column=0)
        # combobox for baudrate
        self.baudrate = tk.IntVar()
        self.baudrate_combobox = ttk.Combobox(self.frame, width=12, textvariable=self.baudrate, state='readonly')
        self.baudrate_combobox['values'] = (4800, 9600, 19200, 38400, 57600, 76800, 460800, 115200)
        self.baudrate_combobox.grid(row=1, column=1)
        self.baudrate_label = ttk.Label(self.frame, text='Baudrate:')
        self.baudrate_label.grid(row=0, column=1)
        # self.button = ttk.Button(self.frame, text='Connect', command=self.connect)
        # self.button.grid(row=0,column=2)
        # combobox for parity
        self.parity = tk.StringVar()
        self.parity_combobox = ttk.Combobox(self.frame, width=12,textvariable=self.parity, state='readonly')
        self.parity_combobox['values'] = ('none', 'even', 'odd')
        self.parity_combobox.grid(row=1, column=2)
        self.parity_label = ttk.Label(self.frame, text='Parity:')
        self.parity_label.grid(row=0, column=2)
        # combobox for bits
        self.bits = tk.IntVar()
        self.bits_combobox = ttk.Combobox(self.frame, width=12,textvariable=self.bits, state='readonly')
        self.bits_combobox['values'] = (8, 7)
        self.bits_combobox.grid(row=1, column=3)
        self.bits_label = ttk.Label(self.frame, text='Bits:')
        self.bits_label.grid(row=0, column=3)
        # combobox for stopbits
        self.stopbits = tk.IntVar()
        self.stopbits_combobox = ttk.Combobox(self.frame, width=12,textvariable=self.stopbits, state='readonly')
        self.stopbits_combobox['values'] = (1,2)
        self.stopbits_combobox.grid(row=3, column=0)
        self.stopbits_label = ttk.Label(self.frame, text='Stop Bits:')
        self.stopbits_label.grid(row=2, column=0)

        # radio buttons for either hex ot ascii command entries
        self.hexradvar = tk.StringVar()
        self.hexradvar.set("ascii")
        self.hexRadButton = tk.Radiobutton(self.frame, text="Hex",
                                           variable=self.hexradvar,
                                           value='hex', command=None)
        self.hexRadButton.grid(row=3, column=1)
        self.asciiRadButton = tk.Radiobutton(self.frame, text="Ascii",
                                             variable=self.hexradvar,
                                             value='ascii', command=None)
        self.asciiRadButton.grid(row=3, column=2)

        # open port button
        self.openButton = ttk.Button(self.frame, text='Open Port', command=self.openport)
        self.openButton.grid(row=3, column=3, sticky='WE')

        # labelframe for I/O echo
        # self.IOframe = ttk.LabelFrame(self.root, text='I/O Echo:')
        # self.IOframe.grid(row=1, column=0) 

        # scrolled text for serial input and output echo
        self.scrolled_text = tk.StringVar()
        self.echoScrolledTextBox = sct.ScrolledText(self.frame, wrap=tk.WORD)
        # debug print
        #self.echoScrolledTextBox.insert(2.0, 'Thaswassup')
        self.echoScrolledTextBox.grid(row=4, column=0, sticky='WE', columnspan=4)

        # send button
        self.sendButton = ttk.Button(self.frame, text='Send', command=self.send)
        self.sendButton.grid(row=5, column=3, sticky='WE')

        # Command textbox
        self.command = tk.StringVar()
        self.command_entered = ttk.Entry(self.frame, textvariable=self.command)
        self.command_entered.grid(row=5, column=0, sticky='WE', columnspan=3)
        self.root.resizable(False, False)

        # Communication related variables
        self._atgmMedia = None

        # a hex converter class
        self.hex_compute = hc.Hex_Computer()


    def openport(self):
        """
        opens serial port
        """
        self._atgmMedia = AC.SerialMedia(unix_path_to_port=self.device_text.get(), baudrate=self.baudrate.get())
        if self._atgmMedia.is_open:
            self.echoScrolledTextBox.insert('[Connected]...\n')
            self._atgmMedia.responseEvent += self._responseRecieved
        else:
            self.echoScrolledTextBox.insert('[Port not found]...\n')
        return

    def send(self):
        """
        Takes in  commands in ascii/hex/
        """
        data_string = self.command.get()
        if self.hexradvar.get() == "hex":
            if self.hex_compute.check_for_hex(data_string):
                data_to_send = self.hex_compute.convert_hex_to_bytes(data_string)
            else:
                msg.showinfo('Value Error','The given command is not in the hex format: please prefix your command with a <0x>, sample command - 0x0123434f')
                return
        else:
            data_to_send = data_string.encode('utf-8')
        self._atgmMedia.send(data_send)
        return

    def _responseRecieved(self, data):
        """
        displays the data recieved onto the output echo box(echoScrolledTextBox)
        """
        self.echoScrolledTextBox.insert('\n'+data+'\n')




    def __populateDeviceCombobox__(self):
        pattern = 'tty.'
        result = ()
        file_path = '/dev/'
        files = os.listdir(file_path)
        for file in files:
            if pattern in file:
                result = result + (file,)
        return result


    def run(self):
        self.root.mainloop()

def main():
    window = Atgm_Diagnostic_GUI()
    window.run()

if __name__ == "__main__":
    main()


