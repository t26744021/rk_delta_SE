- **Project Name**：
    
    Python Connect to Delta-SE Series for "Read" and "Write" Functions <br>

 
- **Optimization Items:**
    
    - **Address Jump Issue:**<br>

        Delta PLC Modbus address planning is discontinuous.<br>
        For example : M1535 (address 0x0Dff) and M1536 (address_0xB000)<br>                                        
        This limits "batch read/write" operations.<br>

    - **Word/Dword Sign:**<br> 

        Add Word/Dword calculations for signed/unsigned.<br>
        

    - **KeepAlive:**<br> 
            
        By default,the Delta PLC will automatically disconnect if no data is send within 120 seconds.<br>
        For example,if the "user" writes a program that makes an indicator light blink alternately every 130 seconds,<br> 
        the PLC will disconnect due to the timeout,add the KeepAlive long-connection feature, users can easily maintain continuous operation and avoid disconnection.<br>


- **Support PLC**：
    
    Detla SE Series (Ethernet)

- **How to use**：

    - **Step-1 : Configure**
        ```python
            IP : 192.168.3.100

        ```

    - **Step-2 : Install rk_delta_SE ( Windows )**
        ```python
        pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl
        ```
        Example : C:\Users\Downloads\rkmcprotocol-main>pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl

    - **Step-2 : Install / Uninstall rk_delta_SE ( Raspberr PI OS 64-bit )**
        ```python
        pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl --break-system-packages
        ```
        ```python
        pip uninstall rk_mcprotocol --break-system-packages
        ```
        Example : rk@raspberrypi:~/rkmcprotocol $ pip install dist/rk_mcprotocol-0.0.2-py3-none-any.whl --break-system-packages<br>

        Example : rk@raspberrypi:~/rkmcprotocol $ pip uninstall rk_mcprotocol --break-system-packages<br>

- **Function Overview**：
 

                                                                    Delta SE : Memory Range
        Function      Device Code      Length        Device Code     Points     CarrySystem   Max.Points 
        -------------------------------------------| --------------------------------------------------
        read_sign_word     D0           100        |      X         X0 ~ X377        8          256    
                                                   |      Y         Y0 ~ Y377        8          256    
                                                   |      M         M0 ~ M4095       10         4096    
                                                   |      S         S0 ~ S1023       10         1024     
        read_sign_Dword    D0           50         |         
                                                   |      D         D0 ~ D11999      10         12000 
                                                   |
                                                   |  
        read_bit           X0           256        |           
                           Y0           256        |        
                           M0           256        |----------------------------------------------------
                           S0           256        |
                                                   |                                                   
        write_sign_word    D0           100        |
                                                   |
                                                   |
                                                   |
        write_sign_Dword   D0           50         |
                                                   | 
                                                   |
                                                   |
        write_bit          Y0           256        |
                           M0           256        |
                           S0           256        |
                                                   |
                                                   |                
        -------------------------------------------|

- **Commands**：
    ```python  

        # Read M0 ~ M255 , Value : 0 or 1
        print(rk_delta_SE.read_bit(s,headdevice = 'M0' , length = 256 ))

        # Read D0 ~ D99              
        # signed_type=True  Value : -32,768 ~ 32,767 
        # signed_type=False Value :       0 ~ 65,535 
        print(rk_delta_SE.read_sign_word(s,headdevice = 'D0' , length = 100, signed_type=True))

        # Read (D0,D1) ~ (D98,D99)  
        # signed_type=True  Value : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False Value :              0 ~ 4,294,967,295       
        print(rk_delta_SE.read_sign_Dword(s,headdevice = 'D0' , length =50 , signed_type=True))
     

        # Write Y0 ~ Y377 , Value : 0 or 1
        print(rk_delta_SE.write_bit(s,headdevice = 'Y0' , data_list = [1]*256 )) 

        # Write D0 ~ D99              
        # signed_type=True  Value : -32,768 ~ 32,767
        # signed_type=False Value :       0 ~ 65,535 
        print(rk_delta_SE.write_sign_word(s,headdevice = 'D0' , data_list = [-999]*100 ,signed_type =True))

        # Write (D0,D1) ~ (D98,D99)  
        # signed_type=True  Value : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False Value :              0 ~ 4,294,967,295       
        print(rk_delta_SE.write_sign_Dword(s,headdevice = 'D0' , data_list = [9999999]*50 ,signed_type =True))


    ```
- **Example**：
    ```python  

        #Example PLC Delta-26SE 

        import rk_delta_SE 
        import time
        
        HOST = '192.168.3.100'
        PORT = 502
        s = rk_delta_SE.open_socket(HOST,PORT) 
 
        while True :
            st = time.time()
            
            print(rk_delta_SE.read_bit(s,headdevice = 'M0' , length = 256 ))
            print(rk_delta_SE.read_sign_word(s,headdevice = 'D0' , length = 100, signed_type=True))
            print(rk_delta_SE.read_sign_Dword(s,headdevice = 'D0' , length =50 , signed_type=True))   
            print(rk_delta_SE.write_bit(s,headdevice = 'Y0' , data_list = [1]*256 )) 
            print(rk_delta_SE.write_sign_word(s,headdevice = 'D0' , data_list = [-999]*100 ,signed_type =True))
            print(rk_delta_SE.write_sign_Dword(s,headdevice = 'D0' , data_list = [9999999]*50 ,signed_type =True))
        
            et = time.time()
            elapsed = et -st
            time.sleep(1)  
            
            print (f' elapsed time = {elapsed}')

    
- **Q&A**：

    - **Why use import threading**
    
        A : After connecting to the Delta PLC , if no message is send within 120 seconds , the Delta PLC
            will automatically disconnect. To maintain a long connection , if the user dose not send a message 
            within 110 seconds , an internal thread will trigger to keep the connection active. 

    - **Why use import time**

        A : The same as above.

    - **Is it faster to use threads?**

        A : Yes <br>
 
        Reference : DVP-ES2/EX2/EC5/SS2/SA2/SX2/SE&TP Operation Manual - Programming (Page B-2)  : <br>
                    Although Modbus TCP operates in half-duplex mode , the PLC itself supports multitasking with 8 available client ports.
               
          ※Note  : While 8 ports are available , it is genrally not recommended to use them all . 
                    Typically,one port is already occupied by the PLC user's connection , User need to know the number of ports in use , otherwise connections may fail .

 