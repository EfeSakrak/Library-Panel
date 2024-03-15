import sqlite3

class Kitap:
    def __init__(self, baslik, yazar, yayin_evi, yayin_yili):
        self.baslik = baslik
        self.yazar = yazar
        self.yayin_evi = yayin_evi
        self.yayin_yili = yayin_yili
        
    def bilgileri_goster(self):
        print(50*"#")
        print(f"Başlık: {self.baslik}\nYazar: {self.yazar}\nYayın Evi: {self.yayin_evi}\nYayın Yılı: {self.yayin_yili}")

class Uye:
    def __init__(self, ad, soyad, uye_numarasi):
        self.ad = ad
        self.soyad = soyad
        self.uye_numarasi = uye_numarasi
        
    def bilgileri_goster(self):
        print(50*"#")
        print(f"Ad: {self.ad}\nSoyad: {self.soyad}\nÜye Numarası: {self.uye_numarasi}")

class Kutuphane:
    def __init__(self):
        self.conn = sqlite3.connect('kutuphane.db')
        self.cursor = self.conn.cursor()
        self._create_tables()
        
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Kitaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baslik VARCHAR(300),
                yazar VARCHAR(100),
                yayin_evi VARCHAR(200),
                yayin_yili DATE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Uyeler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad VARCHAR(100),
                soyad VARCHAR(100),
                uye_numarasi VARCHAR(11)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS OduncKitaplar (
                kitap_id INTEGER,
                uye_id INTEGER,
                FOREIGN KEY (kitap_id) REFERENCES Kitaplar (id),
                FOREIGN KEY (uye_id) REFERENCES Uyeler (id),
                PRIMARY KEY (kitap_id, uye_id)
            )
        ''')
        
        self.conn.commit()
        
    def _get_kitap_id(self, baslik):
        self.cursor.execute('SELECT id FROM Kitaplar WHERE baslik = ?', (baslik,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def _get_uye_id(self, uye_numarasi):
        self.cursor.execute('SELECT id FROM Uyeler WHERE uye_numarasi = ?', (uye_numarasi,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def kitap_ekle(self, kitap):
        self.cursor.execute('INSERT INTO Kitaplar (baslik, yazar, yayin_evi, yayin_yili) VALUES (?, ?, ?, ?)',
                            (kitap.baslik, kitap.yazar, kitap.yayin_evi, kitap.yayin_yili))
        self.conn.commit()
        print(f"{kitap.baslik} kütüphanenize başarılı bir şekilde eklendi.")
        
    def kitap_sil(self, baslik):
        kitap_id = self._get_kitap_id(baslik)
        if kitap_id:
            self.cursor.execute('DELETE FROM Kitaplar WHERE id = ?', (kitap_id,))
            self.conn.commit()
            print(f"{baslik} kütüphanenizden başarılı bir şekilde silindi.")
        else:
            print(f"{baslik} başlıklı kitap bulunamadı")
        
    def uye_ekle(self, uye):
        self.cursor.execute('INSERT INTO Uyeler (ad, soyad, uye_numarasi) VALUES (?, ?, ?)',
                            (uye.ad, uye.soyad, uye.uye_numarasi))
        self.conn.commit()
        print(f"{uye.ad} {uye.soyad} kütüphanenizin üyeleri arasına başarılı bir şekilde eklendi.")
        
    def uye_sil(self, uye_numarasi):
        uye_id = self._get_uye_id(uye_numarasi)
        if uye_id:
            self.cursor.execute('DELETE FROM Uyeler WHERE id = ?', (uye_id,))
            self.conn.commit()
            print(f"{uye_numarasi} kütüphanenizden başarılı bir şekilde silindi.")
        else:
            print(f"{uye_numarasi} numaraya sahip üye bulunamadı")
        
    def odunc_almak(self, baslik, uye_numarasi):
        kitap_id = self._get_kitap_id(baslik)
        uye_id = self._get_uye_id(uye_numarasi)
        if kitap_id and uye_id:
            self.cursor.execute('SELECT * FROM OduncKitaplar WHERE kitap_id = ?', (kitap_id,))
            odunc_durumu = self.cursor.fetchone()
            if odunc_durumu:
                print(f"{baslik} adlı kitap zaten ödünçte. Başka bir kitap seçiniz.")
            else:
                self.cursor.execute('INSERT INTO OduncKitaplar (kitap_id, uye_id) VALUES (?, ?)', (kitap_id, uye_id))
                self.conn.commit()
                print(f"{baslik} adlı kitap {uye_numarasi} kişisi tarafından başarılı bir şekilde ödünç alındı.")
        else:
            print("Yanlış bir kitap veya üye girişi yaptınız.")
    
    def geri_vermek(self, baslik):
        kitap_id = self._get_kitap_id(baslik)
        if kitap_id:
            self.cursor.execute('SELECT * FROM OduncKitaplar WHERE kitap_id = ?', (kitap_id,))
            odunc_durumu = self.cursor.fetchone()
            if odunc_durumu:
                self.cursor.execute('DELETE FROM OduncKitaplar WHERE kitap_id = ?', (kitap_id,))
                self.conn.commit()
                print(f"{baslik} adlı kitap başarılı bir şekilde geri verildi.")
            else:
                print(f"{baslik} adlı kitap zaten ödünçte değil.")
        else:
            print("Yanlış bir kitap girişi yaptınız.")
    
    def kitaplari_goster(self):
        self.cursor.execute('SELECT * FROM Kitaplar')
        kitaplar = self.cursor.fetchall()
        if not kitaplar:
            print("Henüz kütüphanenize eklenmiş bir kitap yoktur.")
        else:
            print("\nKitaplar: ")
            for kitap in kitaplar:
                kitap_obj = Kitap(*kitap[1:])
                kitap_obj.bilgileri_goster()
            
    def uyeleri_goster(self):
        self.cursor.execute('SELECT * FROM Uyeler')
        uyeler = self.cursor.fetchall()
        if not uyeler:
            print("Henüz kütüphanenize eklenmiş bir üye yoktur.")
        else:
            print("\nÜyeler: ")
            for uye in uyeler:
                uye_obj = Uye(*uye[1:])
                uye_obj.bilgileri_goster()
            
    def close_connection(self):
        self.conn.close()

kutuphane = Kutuphane()
while True:
    print(20 * "*", "Kütüphane Yönetim Sistemi Menüsü", 20 * "*")
    print("""
            1. Kitap Ekle
            2. Kitap Sil
            3. Üye Ekle
            4. Üye Sil
            5. Kitap Ödünç Al
            6. Kitap Geri Ver
            7. Kitapları Göster
            8. Üyeleri Göster
            9. Çıkış (q)
    """)
    islem = input("Yapacağınız işlemin numarasını giriniz: ")
    if islem == "1":
        baslik = input("Kitap başlığı: ")
        yazar = input("Yazar: ")
        yayin_evi = input("Yayın evi: ")
        yayin_yili = input("Yayın yılı: ")
        kitap = Kitap(baslik, yazar, yayin_evi, yayin_yili)
        kutuphane.kitap_ekle(kitap)
    elif islem == "2":
        baslik = input("Silmek istediğiniz kitabın adını giriniz: ")
        kutuphane.kitap_sil(baslik)
    elif islem == "3":
        ad = input("Üye adı: ")
        soyad = input("Üye soyadı: ")
        uye_numarasi = input("Üye numarası: ")
        uye = Uye(ad, soyad, uye_numarasi)
        kutuphane.uye_ekle(uye)
    elif islem == "4":
        uye_numarasi = input("Silmek istediğiniz üyenin, üye numarasını giriniz: ")
        kutuphane.uye_sil(uye_numarasi)
    elif islem == "5":
        baslik = input("Kitabın adını giriniz: ")
        uye_numarasi = input("Üye numarasını giriniz: ")
        kutuphane.odunc_almak(baslik, uye_numarasi)
            
    elif islem == "6":
        baslik = input("Kitabın adını giriniz: ")
        kutuphane.geri_vermek(baslik)
            
    elif islem == "7": 
        kutuphane.kitaplari_goster()
    elif islem == "8":
        kutuphane.uyeleri_goster()
    elif islem == "9" or islem == "q" or islem == "Q":
        print("Uygulamadan çıkış yaptınız.")
        break
    else:
        print("Yanlış bir işlem seçimi yaptınız. Lütfen yapmak istediğiniz işlemin sadece numarasını yazınız.")

kutuphane.close_connection()