# @2021.08.20
# 画面上の ActiveWindow の間違い探し画像をスクショして，間違い探しをする。
# @2021.08.20
# 一枚の画像から間違い探しする。
# 絵からマウスで2枚の絵を切り出す。
# @2021.08.23
# 間違い探しの「写真」を載せている人がいる。
# その場合，写真自体が歪んでいるので，画面に2枚の絵を表示しても非常に判りづらい。
# そこで，写真を補正して大体同じにして表示する。
# こうすることで間違いが非常に判りやすくなる。
# @2021.09.04
# 切り出した2つの画像を自動でずらして初期位置を調整する(cv_auto_adjust)。
# 一応これで完成形。

# ----------------------------------------------------------------------
# 使い方
# 1.プログラムを起動する。
# 2.間違い探しの画面で PrintScreen を押下する。
# 　スクショした画面が表示される。
# 3.2つの絵を切り出す。大体同じ大きさに切り出すようにする。
# 　最初の絵の左上でマウス左ボタン押下。
# 　そのまま引きずって右下でマウスボタンを離す。
# 　最初の絵の周りに赤い枠線が表示される。
# 次の絵も同じようにマウスで操作する。
# 　次の絵は青い枠線が表示される。
# 4.この操作終了
# 　ここで何かキー入力する。空白で良い。
# 　ウィンドウが切り替わって絵が1秒毎に交互に表示される。
# ここで直ぐに間違いが見つかればハッピー(自動で差分が小さくなるように表示している)。
# 5.見つからない時，
# 　画像をずらす　→画像サイズが同じ時は大体このパターン
# 　画像を補正する→問題を写真撮影した場合大体補正の必要がある。
# 5.1 画像をずらす方法
# 　上に「=====」が表示されるのが，2番目の画像。
# 　一番目の画像に比べ右に表示されていたら画像を左にずらす(←キー押下)
# 　一番目の画像に比べ左に表示されていたら画像を右にずらす(→キー押下)
# 　一番目の画像に比べ上に表示されていたら画像を下にずらす(↓キー押下)
# 　一番目の画像に比べ下に表示されていたら画像を上にずらす(↑キー押下)
# 　間違い部分以外が一致したら，「+」または「-」キーで画像の切り替え速度を調整する。
# 　速いほうが判りやすい場合もあるし，遅いほうが判りやすい場合もある。
# 　これで場所がわかれば，間違い位置をクリックする。○と番号が表示される。
# 5.2 画像を補正したい場合は以下の手順を追加する。
# 　画像が交互に表示されているが明らかに歪んでいる場合，画像を補正して合わせる必要がある。
# 　そうしないと，酔う(笑)。
# 　交互に表示される画面で，「c」キーを押下すると，別のウィンドウが表示される。
# 　そこで「c」キーを押すと画面が交互に表示される。
# 　両方の画面で同じ場所と考えられる特徴的な部分を4箇所クリックする。
# 　クリックする毎に○と番号が表示される。
# 　両方4箇所ずつクリックするとその画面が終了して，元の画面に戻る。
# 　戻ったとき，画像が補正されて，ずれが殆ど無ければハッピー。
# 　それでもずれがある場合は，画像が反って撮影されたりしているので，それ以上は手立てが無い。
# 　どうしても何とかしたい場合は，その反りの部分だけを選択して間違い探しする(もう一度プログラムを起動し直す必要がある)。
# 6.プログラムを終了する。
# 　matigaisagasi-prtsc.png に間違いをクリックした A の画像が保存される。
# ----------------------------------------------------------------------
# 注意点
# マルチスクリーンでメイン画面以外に問題を表示すると画面キャプチャがうまく行かない。
# 

import time                     # sleep()
import cv2                      # 画像処理
import numpy as np              # 画像処理
from PIL import ImageGrab       # 画面キャプチャ
from pynput import keyboard     # キー入力
import win32gui                 # 最前面Windowを取得

# ----------------------------------------------------------------------
# 4K画面で文字の大きさを150%で表示するよう設定している場合スクリーンショットが
# うまく動かない(領域を間違える)。
# 探したところこれでうまく行く事が判った。もう1つレジストリを書き換える方法も
# 見つかったが，プログラム内から処理できたほうが便利なのでこちらを使用する。
# ----------------------------------------------------------------------
# ↓https://stackoverflow.com/questions/40869982/dpi-scaling-level-affecting-win32gui-getwindowrect-in-python
from ctypes import windll
# Make program aware of DPI scaling
user32 = windll.user32
user32.SetProcessDPIAware()
# ↑おー，感動するな。これでうまく行った。

# ----------------------------------------------------------------------
# ↓キーボード入力コード
# ----------------------------------------------------------------------
KEY_LEFT        = 2424832
KEY_RIGHT       = 2555904
KEY_UP          = 2490368
KEY_DOWN        = 2621440
KEY_ESC         = 27
KEY_PLUS        = 43
KEY_MINUS       = 45
KEY_0           = ord('0')
KEY_1           = ord('1')
KEY_2           = ord('2')
KEY_3           = ord('3')
KEY_4           = ord('4')
KEY_a           = ord('a')
KEY_c           = ord('c')
KEY_q           = ord('q')

# ----------------------------------------------------------------------
# 画面のスクリーンショットを取る。間違い探しの絵が載っている画面を表示して
# PrintScreen キー(普通のキーボードだと右上にある)を押下する。
# ----------------------------------------------------------------------
pnt_rect        = []            # ラバーバンドの2隅。左上と右下。
cv_img          = None          # ラバーバンド表示用
cv_img_org      = None          # ここから切り出す
idx_cut         = 0             # 0 or 1 (2枚の画像用)
cv_cut          = [None,None]   # 切り出した2枚の画像を入れる
color_cut       = [(0,0,255),(255,0,0)] # 2枚の画像切りだし位置に表示する色(1枚目赤,2枚目青),OpenCV は B,G,R の順

def click_and_crop(event, x, y, flags, param):
    """
    ラバーバンドを表示する。
    XORとか使うのでなく，元の画像をコピーし，そこに現在の矩形を描画する。
    で，それを MOUSEMOVE イベント毎に行う。そうすると，前の矩形は表示されない。
    これを繰り返すとマウスドラッグに合わせたラバーバンドを描画することになる。
    なるほど，これで実用的な速度が出るんだ。納得。
    """
    global pnt_rect, cv_img, cv_img_org, idx_cut, cv_cut
    if event == cv2.EVENT_LBUTTONDOWN:
        pnt_rect = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        pnt_rect.append((x, y))
        cv2.rectangle(cv_img, pnt_rect[0], pnt_rect[1], color_cut[idx_cut], 2)
        print(pnt_rect)
        # [lt.y:lt:x, rb:y,rb:x] で取り出す。
        iymin   = min(pnt_rect[0][1],pnt_rect[1][1])
        iymax   = max(pnt_rect[0][1],pnt_rect[1][1])
        ixmin   = min(pnt_rect[0][0],pnt_rect[1][0])
        ixmax   = max(pnt_rect[0][0],pnt_rect[1][0])
        cv_cut[idx_cut]= cv_img_org[iymin:iymax,ixmin:ixmax]
        idx_cut += 1
        if( idx_cut >= 2): idx_cut = 0 # 絵が2枚なんで
        cv2.imshow("image", cv_img)
        #cv2.imwrite('test-draw-rubber-band.cut.png',cv_cut[0])
    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        clone = cv_img.copy()
        cv2.rectangle(clone, pnt_rect[0], (x, y), (0, 255, 0), 2)
        cv2.imshow("image", clone)

def pickup_2images():
    # 既に画像は cv_img に取り込まれていると仮定する。
    # test-matigaisagasi.py はファイル名を引数にファイルを読んだが，
    # このプログラムはスクリーンショットを自ら取得するのでその必要がない。
    global cv_img,cv_img_org
    h,w         = cv_img.shape[:2]
    w_or_h      = 3200
    if( h > w_or_h or w > w_or_h):
        # 絵が大きすぎるとき小さくして表示する。
        if( w >= h):
            neww    = w_or_h
            newh    = round(neww*h/w)
        else:
            newh    = w_or_h
            neww    = round(newh*w/h)
        cv_img      = cv2.resize(cv_img,dsize=(neww,newh))
        h,w         = cv_img.shape[:2]
    cv_img_org  = cv_img.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)
    cv2.imshow("image", cv_img)
    # このままだと このウィンドウが前面に来る事は無い。
    # ↓こうすると前面に出るのだが，「常に前面に表示する」扱いになってしまうので，ちょっと違うかなー。そこまで偉くない。でもやってしまう。
    cv2.setWindowProperty("image", cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(0)              # 画像を2つ切り出したら，何かキー入力して終了する
    cv2.destroyWindow("image")

def cv_pil2cv(im_img):
    ''' PIL型 -> OpenCV型 '''
    # https://qiita.com/derodero24/items/f22c22b22451609908ee
    cv_img      = np.array(im_img, dtype=np.uint8)
    if cv_img.ndim == 2:        # モノクロ
        pass
    elif cv_img.shape[2] == 3:  # カラー
        cv_img  = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
    elif cv_img.shape[2] == 4:  # 透過
        cv_img  = cv2.cvtColor(cv_img, cv2.COLOR_RGBA2BGRA)
    return    cv_img

def save_active_window_screen():
    # 最前面のウィンドウのスクショを取得する
    handle = win32gui.GetForegroundWindow() # 最前面のウィンドウハンドルを取得
    rect = win32gui.GetWindowRect(handle)   # ウィンドウの位置を取得
    print(type(rect),rect)
    screenshot = ImageGrab.grab()              # 'PIL.Image.Image'
    croped_screenshot = screenshot.crop(rect)
    print(type(screenshot))
    print(type(croped_screenshot))
    croped_screenshot.save('screenshot.jpg')
    global cv_img
    cv_img      = cv_pil2cv(croped_screenshot)
    h,w         = cv_img.shape[:2]
    print(f"Capture Size is {w}x{h}")

# ----------------------------------------------------------------------
# キャプチャした絵から2枚の絵を切り出す。
# 切り出したい絵の左上でマウスをダウン，右下まで移動してアップ
# これを2回やる。
# 1回目の矩形に赤い枠線が，2回目の矩形に青い枠線が引かれる。
# 何かキー入力するとこの画面を終了する。
# ----------------------------------------------------------------------
yn_exit_capture = False
def press(key):
    global yn_exit_capture
    if key == keyboard.Key.print_screen:
        save_active_window_screen()
        yn_exit_capture = True

def release(key):
    if key == keyboard.Key.esc:     # escが押された場合
        return False    # listenerを止める

listener = keyboard.Listener(
    on_press=press,
    on_release=release)

print("間違い探し画面を表示し PrintSreen(PrtSc) キーを押してください")
listener.start() # これはここで待ってくれる訳ではない。
import msvcrt
while True: # だから自分でループを作る。
    time.sleep(1)
    if( yn_exit_capture):
        break
listener.stop()                  # 多分こうしないと，以降の waitKey() がうまく動かない

print("スクショした画面から2つの絵を切り出してください")
pickup_2images()

# 2つの画像が取得できたはず。
cv_A = cv_cut[0]
cv_B = cv_cut[1]

if( cv_A is None):
    raise Exception(f"画像 A が取得できていない")
if( cv_B is None):
    raise Exception(f"画像 B が取得できていない")

# ----------------------------------------------------------------------
# 必要に応じて歪みを補正する。
# これらの処理は必要に応じてこれ以降の関数から呼び出される。
# if( view2pics_and_click_rectangle(cv_A,cv_B)):
#     cv_B_new    = hosei4(cv_A,cv_B,pnt_ab) # 合計8点を使ってBを変形する
# ----------------------------------------------------------------------
idx_view        = 0                 # 0 or 1 で表示中の画像を切り替える
cv_ab           = [None,None]       # 将来 cv_A,cv_B を入れる
cnt_ab          = [0,0]             # 何箇所クリックした？
pnt_ab          = [[0]*4,[0]*4]     # それぞれ4箇所クリックできる
idx_view        = 0                 # 0(cv_A) or 1(cv_B)

def click4pos(event,x,y,flags,param):
    global cnt_ab, pnt_ab
    if event == cv2.EVENT_LBUTTONDOWN:
        if( cnt_ab[idx_view] < 4):
            pnt_ab[idx_view][cnt_ab[idx_view]]= (x,y)
            cv_img  = cv_ab[idx_view]
            radius  = 20
            cv2.circle(cv_img,(x,y),radius,(0,255,0),lineType=cv2.LINE_AA,thickness=2)
            cv2.putText(cv_img, f"{cnt_ab[idx_view]+1}", (x-radius,y-radius), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,128,0), thickness=2)
            cnt_ab[idx_view]    += 1

def view2pics_and_click_rectangle(cv_img1,cv_img2):
    """
    2つの図形を表示し，それぞれ一致すると思われる4箇所をクリックしてもらう。
    色々なインタフェースが考えられるが，
    1.'a','b' で図形を切り替える。'c'は図形の切り替えをトグルする。
    2.クリックしたら○を表示し番号を振る。
    3.今のところ訂正機能は無い。
    4.それぞれ4つクリックしたら終了する。
    5.4個超クリックするのは無視する。
    戻り値は 
    True: 全てクリックした(8点)
    False: 途中でキャンセルした。
    """
    global cv_ab, cnt_ab, pnt_ab, idx_view
    winname     = 'click4'
    def exitthis(tf):
        cv2.destroyWindow(winname)
        return    tf
    cv2.namedWindow('click4',cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('click4',click4pos)
    cv_A        = cv_img1.copy() # ○を描いて汚すのでコピーを作成しておく
    cv_B        = cv_img2.copy()
    yn_change   = True          # キーボードから表示する画面を切り替えたとき切り替えまで True にする。最初の表示をするために True を初期値にする。
    ha,wa,      = cv_A.shape[:2] # A,B の大きさ
    hb,wb,      = cv_B.shape[:2] # 大きいほうに Window サイズを合わせる
    cv2.resizeWindow('click4', max(wa,wb), max(ha,hb))     # 画像 A,B の大きいほうに合わせる
    cv_ab       = [cv_A,cv_B]
    while True:
        key     = cv2.waitKeyEx(1)
        if( key == KEY_q or key == KEY_ESC): # 4点全てクリックする前に終了
            return    exitthis(False)
        if( key == ord('a') or key == ord('A')):
            idx_view    = 0     # 表示を A に戻す。厳密にやろうとすれば，切り替えの処理中にクリックしたときとか，idx_view と齟齬が生じる可能性があるが，そこまで厳密にしない。
            yn_change   = True
        if( key == ord('b') or key == ord('B')):
            idx_view    = 1     # 表示を B に切り替える
            yn_change   = True
        if( key == ord('c') or key == ord('C')):
            if(idx_view): idx_view=0 # 図形をトグルする。'a','b'で切り替えるより，トグルできるようにした方が使いやすい。
            else:         idx_view=1
            yn_change   = True
        if( yn_change):         # 表示を切り替える
            cv2.imshow('click4',cv_ab[idx_view])
        if( min(cnt_ab) >= 4):  # 4点をクリックしたら終了
            return    exitthis(True)
    raise Exception("ここに来たらダメでしょ")

def hosei4(cv_A,cv_B,pnt_ab):
    """
    pnt[0]      :Aの4点が (x,y) の形式で入っている
    pnt[1]      :Bの4点が (x,y) の形式で入っている
    cv_B の4点が cv_A の4点に重なるように図形を変形する。
    変形後の図形の大きさは cv_A の大きさになる。
    """
    src         = np.float32(pnt_ab[1]) # Bの4点
    dst         = np.float32(pnt_ab[0]) # Aの4点
    M           = cv2.getPerspectiveTransform(src, dst)
    ha,wa       = cv_A.shape[:2]
    cv_B_new    = cv2.warpPerspective( cv_B, M, (wa, ha))
    return    cv_B_new

# ----------------------------------------------------------------------
# 2つの画像のクリック場所に○を表示て，間違いの個数を勘定していく。
# これしないと直ぐに何処に間違いがあったか忘れてしまう。
# ----------------------------------------------------------------------
radius_clicked  = 30            # 自分で見つけた間違い箇所に○を描く。その時の半径。
inum_clicked    = 0             # 自分で見つけた間違い箇所の個数。○と一緒に表示する。
def click_diff(event,x,y,flags,param):
    global inum_clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        x       -= 100
        y       -= 100
        inum_clicked    += 1
        cv2.circle(cv_A,(x,y),radius_clicked,(0,255,0),lineType=cv2.LINE_AA,thickness=2)
        cv2.putText(cv_A, f"{inum_clicked}", (x-radius_clicked+2,y-radius_clicked+1), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), thickness=2)
        cv2.putText(cv_A, f"{inum_clicked}", (x-radius_clicked,y-radius_clicked), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128,0,0), thickness=2)
        cv2.circle(cv_B,(x-diff_x,y-diff_y),radius_clicked,(0,255,0),lineType=cv2.LINE_AA,thickness=2)
        cv2.putText(cv_B, f"{inum_clicked}", (x-diff_x-radius_clicked+2,y-diff_y-radius_clicked+1), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), thickness=2)
        cv2.putText(cv_B, f"{inum_clicked}", (x-diff_x-radius_clicked,y-diff_y-radius_clicked), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (128,0,0), thickness=2)
        # ↑文字の色を○と同じ色にしたらけばけばし過ぎて見難くかった。だから少々目立たない色にしている。

# ----------------------------------------------------------------------
# 2つの絵が重なるように自動で位置を調整する。
# ----------------------------------------------------------------------
def cv_auto_adjust(cv_A,cv_B):
    """
    cv_A がベース画像，cv_B を動かしてみる。
    画像のずれ(absdiff())が最小になるようにX方向を調べ，次にY方向を調べる。
    全ての可能性を調べているわけではないので，うまくいかない場合もある。
    """
    ha,wa           = cv_A.shape[:2]
    hb,wb           = cv_B.shape[:2]
    w               = max(wa,wb)+100*2
    h               = max(ha,hb)+100*2
    cv_ban          = np.ones((h, w, 3), np.uint8)*[255,255,255] # cv_A,cv_B の両方が納まる盤面を作成する
    cv_banA         = cv_ban.copy()
    cv_banA[100:ha+100, 100: wa+100] = cv_A # cv_A を上下左右に100の余裕を持って配置する

    ix,iy           = 0,0
    sumv            = h*w*255*3 # absdiff() を計算したとき最大になる値。「*3」は三色分
    ixmin           = 0
    for ix in range(-30,31):    # cv_B をX方向に-30から30まで動かしてみる
        cv_banB     = cv_ban.copy()
        cv_banB[100+iy:hb+100+iy, 100+ix: wb+100+ix] = cv_B
        cv_diff2        = cv2.absdiff(cv_banA,cv_banB)
        v           = np.sum(cv_diff2) # cv_Aとcv_Bの一致度が高いほど小さい値(背景が黒の画像)になる
        print("ix",v,ix)               # 動いているのが分かるように出力
        if( v < sumv):          # 一致度が高い方を
            ixmin   = ix        # 記録していく
            sumv    = v
    ix              = ixmin     # X方向に画像をずらしてこの位置が一致度が一番高かった
    # ↓上と同じように Y 方向についてもやってみる。X方向は上で見つかった最適値のまま固定して作業する。
    sumv            = h*w*255*3
    iymin           = 0
    for iy in range(-30,31):    # Y方向-30から30まで動かしてみる，X方向は上で計算済み
        cv_banB     = cv_ban.copy()
        cv_banB[100+iy:hb+100+iy, 100+ix: wb+100+ix] = cv_B
        cv_diff2        = cv2.absdiff(cv_banA,cv_banB)
        v           = np.sum(cv_diff2) 
        print("iy",v,iy)
        if( v < sumv):
            iymin   = iy
            sumv    = v
    print(f"ix:{ixmin}, iy:{iymin}")
    iy              = iymin
    # X方向，Y方向の順にずらして決めた値。
    # これが正解とは限らないが，殆どの場合これで良い。
    # 上の処理では X方向61通り，Y方向61通りで調べたが，
    # X方向*Y方向(61*61通り)調べた方が精度が高くなるが，遅くなるのでやらない。
    # (ixmin,iymin)から更に微調整が必要な場合もあるが，作業する気力が無い！
    # やるとしたら，(ixmin,iymin)が↓のXの位置だとして，12345678の場所に移動してabsdiff()を計算し，最小値を更新しなくなるまで続ける。
    # 123 
    # 4X5
    # 678
    return    (ixmin,iymin)

# ----------------------------------------------------------------------
# この2つの画像を時間差で重ねて表示し，見た目で違いを判断する。
# 但し歪んだ図形(写真)の場合，別処理で歪みを補正する。
# ----------------------------------------------------------------------
# 2つの絵の大きさは？
ha,wa           = cv_A.shape[:2]
hb,wb           = cv_B.shape[:2]
mouseX          = [0,wb,0,wb]
mouseY          = [0,0,hb,hb]
# 周りに余裕を持たせるため，表示領域は上下左右100ピクセル広げる。
# 今は A の絵だけでそれを行う。本当は大きいほうの絵を使うべきだが面倒なので。
w               = max(wa,wb)+100*2
h               = max(ha,hb)+100*2
print('A:',wa,ha)
print('B:',wb,hb)

cv2.namedWindow("A", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("A", click_diff)
cv2.resizeWindow('A', w, h)     # 画像 A,B の大きいほうに合わせる

cv_ban          = np.ones((h, w, 3), np.uint8)*[255,255,255] # 白で盤面を調整する

diff_x          = 0
diff_y          = 0
istat           = 0             # 0:移動する，1:変形する(補正する)
ipoint          = 0             # 0:無効,1-4:四角形の左上からZの順

diff_x,diff_y   = cv_auto_adjust(cv_A,cv_B)

def prockey(key):               # 
    # B の画像を移動または変形する
    # 実際には移動の処理は別に行う。
    global diff_x, diff_y,waitmsec,istat,cv_B_org,cv_B,cv_A,mouseX,mouseY,ipoint,wb,hb
    # 現在の状態で処理を分ける。
    if( key == KEY_LEFT):
        diff_x  -= 1
    elif( key == KEY_RIGHT):
        diff_x  += 1
    elif( key == KEY_UP):
        diff_y  -= 1
    elif( key == KEY_DOWN):
        diff_y  += 1
    elif( key == KEY_PLUS):
        waitmsec-= 100
        if( waitmsec < 100):
            waitmsec    = 100   # 最小値は100にする。
            print(f"{waitmsec}msec:これ以上速く切り替えできません")
        else:
            print(f"{waitmsec}msec 切り替え")
    elif( key == KEY_MINUS):
        waitmsec+= 100
        print(f"{waitmsec}msec 切り替え")
    if( key == ord('p')):       # 現在の2枚の画像をA.jpg,B.jpg として出力する(デバッグ用途)
        cv2.imwrite('A.jpg',cv_A)
        cv2.imwrite('B.jpg',cv_B)
    elif( key == KEY_c):        # 'c' で別ウィンドウを表示して絵を補正する
        # 写真(イラストでない)の場合 画像を平行移動しただけでは同じ位置に揃わないので，変形することを考える。
        if( view2pics_and_click_rectangle(cv_A,cv_B_org)):
            # 2つの写真の同じ場所と思しき場所を4点ずつクリックする。
            cv_B    = hosei4(cv_A,cv_B,pnt_ab) # 合計8点を使ってBを変形する
            hb,wb   = cv_B.shape[:2]
    elif( key == KEY_a):
        diff_x,diff_y   = cv_auto_adjust(cv_A,cv_B)

waitmsec        = 1000          # 最初は1秒(1000ミリ秒)毎に絵を切り替える
cv_B_org        = cv_B.copy()   # 変形は最初の形を覚えている必要があるので
# キーボード操作で画像の状態を変化させる。
# 以下の2つの状態を持つ。
# Bを移動する状態
# Bを変形する状態(Aの画像に合わせて補正する)
# 画像Aは移動も変形もしない。
while(1):
    cv_ban[100:ha+100, 100: wa+100] = cv_A
    # ↓位置は適当。画像Bを表示するとき = を出力しているので，Aは空白を表示してどちらを表示しているか判るようにしている。
    cv_ban      = cv2.rectangle(cv_ban, (50, 50 - 20), (50 + 130, 50), (255,255,255), -1)
    # ↓空白を出力しても色は付かない。だから何も書かないと一緒なので，↑で白い矩形を表示するようにした。
    #cv2.putText(cv_ban, f'          ', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,128), thickness=2)
    cv2.imshow('A',cv_ban.astype(np.uint8))
    key         = cv2.waitKeyEx(waitmsec)
    if( key == KEY_ESC):
        break
    elif( key != -1):
        prockey(key)
    cv_ban[100+diff_y:hb+diff_y+100, 100+diff_x: wb+diff_x+100] = cv_B
    # ↓本当は●を色付きで表示しようと思ったが，OpenCV(cv2)が漢字に対応していないため，適当な半角文字列
    # 　これ(=====)がチカチカしている方が2枚目の画像なので，矢印キーで一枚目の画像に合わせるように移動する。
    cv2.putText(cv_ban, f'=====', (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), thickness=2)
    cv2.imshow('A',cv_ban.astype(np.uint8))
    key         = cv2.waitKeyEx(waitmsec)
    if( key == KEY_ESC):
        break
    elif( key != -1):
        prockey(key)

cv2.destroyWindow('A')      # これをしないと Jupyter で Window が消えずストールする
fn_output       = 'matigaisagasi-prtsc.png'   # 結果を書き込むファイル名。cv2は漢字を使えない。
cv2.imwrite(fn_output,cv_A) # 最後に答え(自分で番号振ったやつ)を出力する
print(f"{fn_output} に結果を出力しました。")
