- **項目名稱**：
    
    Python 連接 PLC Delta-SE系列，實現"讀取"和"寫入"功能<br>



- **優化項目:**

    - **跳址問題:**<br>

        Delta PLC 的 Modbus 地址（如 M/D 元件）並非連續排列<br>
        例如：M1535(address_0x0DFF) 與 M1536(address_0xB000)<br>
        這樣會限制"批量讀取/批量寫入"的操作。<br>

    - **Word/Dword正負符號:**<br>

        加入 Word/Dword,讀取/寫入正負符號計算。

    - **Dword計算:**<br>
    
        加入 Dword 的讀取/寫入計算。
    
    - **KeepAlive長連線:**<br>
        
        Delta PLC 預設當連線閒置超過 120 秒未傳送訊號時，將自動斷線。例如，若「使用者」編成程式:每 130 秒
        交替閃爍指示燈，則會因超時而被 PLC 切斷連線。除非使用者採取其他方法維持長連線。

- **支援 PLC**：
    
    Detla SE 系列 (Ethernet)

- **使用步驟**：

    - **步驟-1 : 設定PLC環境**
        ```python
            IP : 192.168.3.100
        ```

    - **步驟-2 : 安裝 rk_delta_SE ( Windows )**
        ```python
        pip install dist/rk_delta_SE-0.0.1-py3-none-any.whl
        ```

    - **步驟-2 : 安裝 / 移除 rk_delta_SE ( Raspberr PI OS 64-bit )**
        ```python
        pip install dist/rk_delta_SE-0.0.1-py3-none-any.whl --break-system-packages
        ```
        ```python
        pip uninstall rk_delta_SE --break-system-packages
        ```
        Example : rk@raspberrypi:~/Desktop/rk_delta_SE-main $ pip install dist/rk_delta_SE-0.0.1-py3-none-any.whl --break-system-packages<br>

        Example : rk@raspberrypi:~/Desktop/rk_delta_SE-main $ pip uninstall rk_delta_SE --break-system-packages<br>

- **功能簡介**：
 

                                                               Delta SE : 出廠默認記憶體範圍
        FUNCTION         元件清單      資料長度         元件清單       資料長度        進制       總點數
        -------------------------------------------| --------------------------------------------------
        read_sign_word     D0           100        |      X         X0 ~ X377        8        256    
                                                   |      Y         Y0 ~ Y377        8        256    
                                                   |      M         M0 ~ M4095       10       4096    
                                                   |      S         S0 ~ S1023       10       1024     
        read_sign_Dword    D0           50         |         
                                                   |      D         D0 ~ D11999      10       12000 
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

- **指令**：
    ```python  

        # 讀M0 ~ M255 , 數值 : 0 or 1
        print(rk_delta_SE.read_bit(s,headdevice = 'M0' , length = 256 ))

        # 讀D0 ~ D99              
        # signed_type=True  數值 : -32,768 ~ 32,767 
        # signed_type=False 數值 :       0 ~ 65,535 
        print(rk_delta_SE.read_sign_word(s,headdevice = 'D0' , length = 100, signed_type=True))

        # 讀(D0,D1) ~ (D98,D99)  
        # signed_type=True  數值 : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False 數值 :              0 ~ 4,294,967,295       
        print(rk_delta_SE.read_sign_Dword(s,headdevice = 'D0' , length =50 , signed_type=True))
     

        # 寫Y0 ~ Y377 , 數值 : 0 or 1
        print(rk_delta_SE.write_bit(s,headdevice = 'Y0' , data_list = [1]*256 )) 

        # 寫D0 ~ D99              
        # signed_type=True  數值 : -32,768 ~ 32,767
        # signed_type=False 數值 :       0 ~ 65,535 
        print(rk_delta_SE.write_sign_word(s,headdevice = 'D0' , data_list = [-999]*100 ,signed_type =True))

        # 寫(D0,D1) ~ (D98,D99)  
        # signed_type=True  數值 : -2,147,483,648 ~ 2,147,483,647 
        # signed_type=False 數值 :              0 ~ 4,294,967,295       
        print(rk_delta_SE.write_sign_Dword(s,headdevice = 'D0' , data_list = [9999999]*50 ,signed_type =True))


    ```
- **範例**：
    ```python  

        #Example Delta-26SE

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

    - **為何使用 : import threading**
    
        A : 連線Detla PLC後超過超過120秒，若未再次發送任何訊息，Detla PLC將會主動斷開連線，
            所以為了保持長連線模式，若使用者在110秒內無發送訊息，內部threading將會觸發保持連線<br>

    - **為何使用 : import time**

        A : 同上

    - **使用Threading會比較快嗎?**

         A : 會 <br>
        引用 : DVP-ES2/EX2/SS2/SA2/SX2/SE&TP 操作手册-程序篇 Page (B-2)  :<br>
               雖然ModbusTCP屬於半雙工模式。但PLC本身提供8個Client Port 可多工處理<br>
               
       ※注意： 雖然有 8 個連接埠可用，但一般不建議全部使用。
                通常情況下，PLC 用戶的連接已佔用一個連接埠，使用者需要知道使用中的連接埠數目，否則連接可能會失敗。        