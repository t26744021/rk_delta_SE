import socket
import time 
import threading


keep_alive_count = 1

 
element_table = {"X":[b"\x02",8,1024,b'\x0f'],
                 "Y":[b"\x01",8,1280,b'\x0f'],
                 "S":[b"\x01",10,0,b'\x0f'],
                 "M":[b"\x01",10,2048,b'\x0f',43520,1536],
                 "D":[b"\x03",10,4096,b'\x10',32768,4096]}
modbus_tcp_error_message = {
    "01" : "Illegal Function: The slave device received an unrecognized or unsupported function code. ModbusTCP_error_code = 01(hex)",
    "02" : "Illegal Data Address: The requested register or coil address is unavailable or out of the slave device's address range. ModbusTCP_error_code = 02(hex)",  
    "03" : "Illegal Data Value: The written data value exceeds the allowable range of the register or contains invalid values. ModbusTCP_error_code = 03(hex)",
    "04" : "Slave Device Failure: The slave device encountered an unrecoverable error while processing the request, typically due to hardware failure or other critical errors. ModbusTCP_error_code = 04(hex)",
    "05" : "Acknowledge: The request has been received and is being processed, but it will take longer to complete. ModbusTCP_error_code = 05(hex)",
    "06" : "Slave Device Busy: The slave device is busy processing a previous request and cannot handle the current request. ModbusTCP_error_code = 06(hex)",
    "08" : "Memory Parity Error: The slave device detected a parity error in memory, typically used for diagnostics and error detection. ModbusTCP_error_code = 08(hex)",
    "0A" : "Gateway Path Unavailable: The request was sent through a gateway device, but the gateway path is unavailable. ModbusTCP_error_code = 0A(hex)",
    "0B" : "Gateway Target Device Failed to Respond: The request was sent through a gateway device, but the target device did not respond. ModbusTCP_error_code = 0B(hex)",
}

check_list_headevice =  {"S":["1023",10,256] , "X":["377",8,256] , "Y":["377",8,256] , "M":["4095",10,256] , "D":["11999",10,100]}

class ValidationError(Exception):
    pass

class Datavalitor :
    def __init__(self,def_name,headdevice,length=None,data_list=None,signed_type=None):
        self.def_name = def_name
        self.headdevice = headdevice
        self.length = length
        self.data_list = data_list 
        self.signed_type = signed_type 
    
    def validate(self):
        self._validate_headdevice()
        self._validate_length()
        self._validate_data_list()
        self._validate_signed_type()
        return "OK"

    def _validate_headdevice(self):
        global max_length
        try :
            headdeviec_key = self.headdevice[0].upper()
            
            if not  headdeviec_key  in check_list_headevice :
                raise ValidationError (f"Invalid headdevice_type = {self.headdevice}")
            
            value = check_list_headevice.get(headdeviec_key)
            str_headdevice_max_point , carry_system , max_length = value[0],value[1],value[2]
            str_headdevice_value = self.headdevice[1:] 
 
 
            if not 0 <= int(str_headdevice_value,carry_system) <= int(str_headdevice_max_point,carry_system) :
                raise ValidationError (f"Invalid headdevice_type = {self.headdevice}")
            
        except :
            raise ValidationError (f"Invalid headdevice_type = {self.headdevice}")
        
         
    def _validate_length(self):
        global max_length

        if not self.length == None :
            if  isinstance(self.length,int) and 1 <= self.length <= max_length:
                pass
            else :    
                raise ValidationError (f"Invalid length or length exceeds limit") 
        
    def _validate_data_list(self):
        global max_length
     
        if not self.data_list == None :
            if  isinstance(self.data_list,list) and 1 <= len(self.data_list) <= max_length:
                pass
            else :    
                raise ValidationError (f"Invalid Data_list or Data_list length exceeds limit") 
        
    def _validate_signed_type(self):
        
        try :
            if self.signed_type == None :
                if self.def_name == "write_bit"  :
                    if not self.headdevice[0].upper() in ["S","X","Y","M"] :
                        raise ValidationError
                    if not all(i in [0,1] for i in self.data_list)  :
                        raise ValidationError 
                elif self.def_name == "read_bit" :
                    if not self.headdevice[0].upper() in ["S","X","Y","M"] :
                        raise ValidationError
                
            elif self.signed_type != None :
                if  self.def_name == "write_sign_word" and self.headdevice[0].upper() in ["D"]:
                    b"".join(int.to_bytes(i,2,byteorder="big",signed=self.signed_type) for i in self.data_list) 
                elif  self.def_name == "write_sign_Dword" and self.headdevice[0].upper() in ["D"] :
                    b"".join(int.to_bytes(i,4,byteorder="big",signed=self.signed_type) for i in self.data_list)
                elif self.def_name == "read_sign_word" :
                    if not self.headdevice[0].upper() in ["D"] :
                        raise ValidationError
                elif self.def_name == "read_sign_Dword" :
                    if not self.headdevice[0].upper() in ["D"] :
                        raise ValidationError
                else :
                    raise ValidationError
        except :
                raise ValidationError (f"Invalid data_list or Function and headdevice parameters do not match")  

def open_socket(HOST, PORT):
 
    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.settimeout(6)  
  
        threading.Thread(target=keep_alive, args=(s,), daemon=True).start()
    except (Exception,socket.error) as e :
        print (e)
    return s

def keep_alive(s):
    global keep_alive_count
    while True :
        time.sleep(55) #120 /2 
 
        
        if keep_alive_count == 1 :
            try :
                s.send(b'\x00\x01\x00\x00\x00\x06\x01\x01\x05\x00\x00\x01')   
            except socket.error as e :
                print(f"Keep-alive failed: {e}")
                break 
        else :
           keep_alive_count = 1
            
def modbus_error_message (indata):
    error_code_str = f"{indata[-1]:02x}"
    result = modbus_tcp_error_message.get(error_code_str)
    
    return result

def readmode_full_data_(headdevice , length ,chang_start_address=False ) :
    
    headdevice = headdevice.upper()
    values = element_table.get(headdevice[0])
    
    if chang_start_address == False:
        Function_Code_byte , Oct_or_Dec , start_address = values[0],values[1],values[2]
    
    if chang_start_address == True:
        Function_Code_byte , Oct_or_Dec , start_address = values[0],values[1],values[4]
     
    Start_Register_Addr_byte = int.to_bytes(start_address + int(headdevice[1:],Oct_or_Dec),2)
    Data_byte = int.to_bytes(length,2)
    length_byte = int.to_bytes(len(b'\x01' + Function_Code_byte + Start_Register_Addr_byte + Data_byte),2)
    
    result = b'\x00\x01\x00\x00' + length_byte + b'\x01' + Function_Code_byte + Start_Register_Addr_byte + Data_byte
 
    return result

def writemode_full_data (def_name,headdevice,data_list,signed_type=None,chang_start_address=False) :
    
    headdevice = headdevice.upper()
    values = element_table.get(headdevice[0])
    
    if chang_start_address == False:
        Oct_or_Dec , start_address , Function_Code_byte = values[1],values[2],values[3]
    
    if chang_start_address == True:
       Oct_or_Dec , start_address , Function_Code_byte = values[1],values[4],values[3]
                    
    start_register_address_byte = int.to_bytes(start_address + int(headdevice[1:],Oct_or_Dec),2)
    
    match def_name :
    
        case "write_bit" :  
            quotient = len(data_list)//8
            remainder = len(data_list)%8
        
            if remainder != 0 :
                length =  quotient +1 
            else :
                length = quotient
            register_values_byte = int.to_bytes(int("".join(map(str,data_list))[::-1],2),length,byteorder="little")
            data_byte = int.to_bytes(len(data_list),2)
        case "write_sign_word" :
            register_values_byte = b"".join(int.to_bytes(i,2,byteorder="big",signed=signed_type) for i in data_list)
            data_byte = int.to_bytes(len(data_list),2)
        case "write_sign_Dword":
            register_values_big_byte = b"".join(int.to_bytes(i,4,byteorder="little",signed=signed_type) for i in data_list)
            register_values_byte     = b"".join(register_values_big_byte[i:i+2][::-1] for i in range (0,len(register_values_big_byte),2))
           
            data_byte = int.to_bytes(len(data_list)*2,2)
            
    byte_count = int.to_bytes(len(register_values_byte))    
    length_byte = int.to_bytes(len(b'\x01'+ Function_Code_byte + start_register_address_byte + data_byte + byte_count + register_values_byte),2)
    result = b'\x00\x01\x00\x00' + length_byte + b'\x01' + Function_Code_byte + start_register_address_byte + data_byte + byte_count + register_values_byte
 
    return result

def readmode_indata_analysis (def_name,indata,length,signed_type=None) :
    register_values = indata[9:]

    match def_name :
        
        case "read_bit" :
            coil_values = int.from_bytes(register_values,byteorder="little") 
            result = [( coil_values >> i) & 1 for i in range(length)]
        case "read_sign_word":
            result = [int.from_bytes(register_values[i:i+2],byteorder ="big",signed = signed_type) for i in range(0,len(register_values),2)]
        case "read_sign_Dword":                           
            register_values_little_byte = ( b"".join(register_values[i:i+2][::-1] for i in range (0,len(register_values),2)))
            result = [int.from_bytes(register_values_little_byte[i:i+4],byteorder="little",signed=signed_type) for i in range(0,len(register_values_little_byte),4)]
        case "read_across_address_sign_Dword":
            result = [int.from_bytes(register_values[i:i+2],byteorder ="big",signed = signed_type) for i in range(0,len(register_values),2)]
    
    return result

def send_and_recv (s,def_name,outdata,length,signed_type=None):
    global keep_alive_count
    
    
    s.send(outdata)
    indata =  s.recv(4096)
    keep_alive_count = 0
    
    if len(indata) == 9 :
        result = modbus_error_message (indata)
 
    elif len(indata) > 9 : 
        match def_name :
            case "read_bit":
                result = readmode_indata_analysis (def_name,indata,length)
            case "read_sign_word" :
                result = readmode_indata_analysis (def_name,indata,length,signed_type)
            case "read_sign_Dword":
                result = readmode_indata_analysis (def_name,indata,length,signed_type)
            case "read_across_address_sign_Dword":
                result = readmode_indata_analysis (def_name,indata,length,signed_type)   
            case "write_bit":
                result = "OK"
            case "write_sign_word":
                result = "OK"
            case "write_sign_Dword":
                result = "OK"
    
    return result
    
def handle_read_or_write_across_address_ask_2_time_result(def_name,step1_result,step2_result,signed_type=None):
 
    if def_name in ("read_bit" , "read_sign_word" ) :

        result = step1_result + step2_result
    
    elif def_name == "read_across_address_sign_Dword" :
    
        one_word_result_int = step1_result + step2_result
        result_byte = b"".join(int.to_bytes(i,2,byteorder="little",signed=signed_type)for i in one_word_result_int)
        result =  [int.from_bytes(result_byte[i:i+4][::-1],byteorder="big",signed=signed_type)for i in range(0,len(result_byte),4)]

    elif def_name in ("write_bit" , "write_sign_word" , "write_sign_Dword") :
            
        result ="OK"
    
    return result
    
def read_or_write_across_address_ask_2_time(s,def_name,headdevice,length,signed_type=None,data_list=None):
    
    headdevice = headdevice.upper()
    value = element_table.get(headdevice[0])
    chang_start_headdevice = value[5]
    
    step1_chang_start_address = False
    step1_headdevice = headdevice
    step1_length = (length - ((int(headdevice[1:]) + length)  - chang_start_headdevice ) )

    step2_chang_start_address = True
    step2_headdevice = headdevice[0] + str(chang_start_headdevice)
    step2_length = (((int(headdevice[1:]) + length)  - chang_start_headdevice ) )

    if  def_name in ("read_bit" , "read_sign_word","read_across_address_sign_Dword") :
        
        step1_outdata = readmode_full_data_(headdevice = step1_headdevice , length = step1_length , chang_start_address = step1_chang_start_address)
        step2_outdata = readmode_full_data_(headdevice = step2_headdevice , length = step2_length , chang_start_address = step2_chang_start_address)
    
    elif def_name in ("write_bit" , "write_sign_word",) :
        step1_data_list = data_list[0:step1_length]
        step2_data_list = data_list[step1_length:]
        
        step1_outdata = writemode_full_data (def_name,headdevice=step1_headdevice ,data_list=step1_data_list,signed_type=signed_type,chang_start_address=step1_chang_start_address)
        step2_outdata = writemode_full_data (def_name,headdevice=step2_headdevice ,data_list=step2_data_list,signed_type=signed_type,chang_start_address=step2_chang_start_address)
   
    elif def_name in ("write_sign_Dword") :    
        
        register_values_byte = writemode_full_data(def_name,headdevice=headdevice ,data_list=data_list,signed_type=signed_type,chang_start_address=step1_chang_start_address)
        
        register_data_list =  [int.from_bytes(register_values_byte[13:][i:i+2],byteorder="big",signed=signed_type) for i in range (0,len(register_values_byte[13:]),2)]
        
        step1_data_list = register_data_list[0:step1_length]
        step2_data_list = register_data_list[step1_length:]           

        step1_outdata = writemode_full_data (def_name="write_sign_word",headdevice=step1_headdevice ,data_list=step1_data_list,signed_type=signed_type,chang_start_address=step1_chang_start_address)
        step2_outdata = writemode_full_data (def_name="write_sign_word",headdevice=step2_headdevice ,data_list=step2_data_list,signed_type=signed_type,chang_start_address=step2_chang_start_address)
   
    step1_result = send_and_recv(s,def_name ,step1_outdata,step1_length,signed_type)
    step2_result = send_and_recv(s,def_name ,step2_outdata,step2_length,signed_type)    
        
    result = handle_read_or_write_across_address_ask_2_time_result (def_name,step1_result,step2_result,signed_type)
 
    return result    
    
def read_bit(s,headdevice , length):
    def_name = read_bit.__name__
    try :
        check_list = Datavalitor(def_name,headdevice,length,data_list=None,signed_type=None).validate()
        
        if check_list == "OK" :
            if  headdevice[0].upper() == "M"  and  int(headdevice[1:]) + length > 1536 :
                
                if int(headdevice[1:]) > 1535 :
                    chang_start_address = True
                    outdata = readmode_full_data_(headdevice,length,chang_start_address)
                    result = send_and_recv(s,def_name,outdata,length)
                else :
                    result = read_or_write_across_address_ask_2_time(s,def_name,headdevice,length)
                
            else :    
                outdata = readmode_full_data_(headdevice,length)
                result = send_and_recv(s,def_name,outdata,length)
        else :
            result = check_list
    except (Exception,socket.error) as e :
        result = f"{e.__class__.__name__} - {e} - Function-Name : {def_name} "
 
    return result

def read_sign_word(s,headdevice , length ,signed_type):
    def_name = read_sign_word.__name__
    try :
        check_list = Datavalitor(def_name,headdevice,length,data_list=None,signed_type=signed_type).validate()
        
        if check_list == "OK" :
            if  headdevice[0].upper() == "D"  and  int(headdevice[1:]) + length > 4096 :
                
                if int(headdevice[1:]) > 4095 :    
                    chang_start_address = True
                    outdata = readmode_full_data_(headdevice,length,chang_start_address)
                    result = send_and_recv(s,def_name,outdata,length,signed_type)
                else :
                    result = read_or_write_across_address_ask_2_time(s,def_name,headdevice,length,signed_type)
            else : 
                outdata = readmode_full_data_(headdevice,length)
                result = send_and_recv(s,def_name,outdata,length,signed_type)
        else :
            result = check_list            
    except (Exception,socket.error) as e :
        result = f"{e.__class__.__name__} - {e} - Function-Name : {def_name} "

    return result

def read_sign_Dword(s,headdevice , length ,signed_type):
    def_name = read_sign_Dword.__name__ 
    try :
        check_list = Datavalitor(def_name,headdevice,length,data_list=None,signed_type=signed_type).validate()
        
        if check_list == "OK" :
            if  headdevice[0].upper() == "D"  and  int(headdevice[1:]) + length*2 > 4096 :
                    
                if int(headdevice[1:]) > 4095 :    
                    chang_start_address = True
                    outdata = readmode_full_data_(headdevice,length*2,chang_start_address)
                    result = send_and_recv(s,def_name,outdata,length,signed_type)
                else :
                    def_name = "read_across_address_sign_Dword"  
                    result = read_or_write_across_address_ask_2_time(s,def_name,headdevice,length*2,signed_type)
            else : 
                outdata = readmode_full_data_(headdevice,length*2)
                result = send_and_recv(s,def_name,outdata,length,signed_type)
        else :
            result = check_list 
    
    except (Exception,socket.error) as e :
        result = f"{e.__class__.__name__} - {e} - Function-Name : {def_name}"     
    
    return result

def write_bit(s,headdevice,data_list ) :
    def_name = write_bit.__name__
    length = len(data_list)
    try :
        check_list = Datavalitor(def_name,headdevice,length,data_list=data_list,signed_type=None).validate()
        
        if check_list == "OK" :
            if  headdevice[0].upper() == "M"  and  int(headdevice[1:]) + length > 1536 :
                if int(headdevice[1:]) > 1535 :
                    chang_start_address = True
                    outdata = writemode_full_data (def_name,headdevice,data_list,None,chang_start_address)
                    result = send_and_recv(s,def_name,outdata,length=None,signed_type=None)
                else :
                    result = read_or_write_across_address_ask_2_time(s,def_name,headdevice,length,None,data_list)
                    
            else :
                outdata = writemode_full_data (def_name,headdevice,data_list)
                result =  send_and_recv(s,def_name,outdata,length=None,signed_type=None) 
        else :
            result = check_list 
                
    except (Exception,socket.error) as e :
        result = f"{e.__class__.__name__} - {e} - Function-Name : {def_name}"     
 
    return result 

def write_sign_word(s,headdevice,data_list ,signed_type ) :
    def_name = write_sign_word.__name__
    length = len(data_list)
    try :
        check_list = Datavalitor(def_name,headdevice,length,data_list=data_list,signed_type=signed_type).validate()
        
        if check_list == "OK" :
            if  headdevice[0].upper() == "D"  and  int(headdevice[1:]) + length > 4096 :   
                if int(headdevice[1:]) > 4095 :    
                    chang_start_address = True
                    outdata = writemode_full_data (def_name,headdevice,data_list,signed_type,chang_start_address)
                    result = send_and_recv(s,def_name,outdata,length=None,signed_type=None)
                else :
                    result = read_or_write_across_address_ask_2_time(s,def_name,headdevice,length,signed_type,data_list)
            else :
                outdata = writemode_full_data (def_name,headdevice,data_list,signed_type)
                result =  send_and_recv(s,def_name,outdata,length=None,signed_type=None) 
        else :
            result = check_list 
    except (Exception,socket.error) as e :
        result = f"{e.__class__.__name__} - {e} - Function-Name : {def_name}"
    
    return result 
 
def write_sign_Dword(s,headdevice,data_list ,signed_type ) :
    def_name = write_sign_Dword.__name__
    length = len(data_list)*2
    
    try :
        check_list = Datavalitor(def_name,headdevice,length,data_list=data_list,signed_type=signed_type).validate()
        
        if check_list == "OK" :
            if  headdevice[0].upper() == "D"  and  int(headdevice[1:]) + length > 4096 :
                if int(headdevice[1:]) > 4095 : 
                    chang_start_address = True
                    outdata = writemode_full_data (def_name,headdevice,data_list,signed_type,chang_start_address)
                    result = send_and_recv(s,def_name,outdata,length=None,signed_type=None)
                else :
                    result = read_or_write_across_address_ask_2_time(s,def_name,headdevice,length,signed_type,data_list)
            else :
                outdata = writemode_full_data (def_name,headdevice,data_list,signed_type)
                result =  send_and_recv(s,def_name,outdata,length=None,signed_type=None)  
        else :
            result = check_list 
    except (Exception,socket.error) as e :
        result = f"{e.__class__.__name__} - {e} - Function-Name : {def_name}"        
        
    return result 

 