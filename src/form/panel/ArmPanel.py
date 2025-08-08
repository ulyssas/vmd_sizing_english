# -*- coding: utf-8 -*-
#
import wx
import wx.lib.newevent
import numpy as np

from form.panel.BasePanel import BasePanel
from form.parts.FloatSliderCtrl import FloatSliderCtrl
from form.parts.SizingFileSet import SizingFileSet
from module.MMath import MRect, MVector3D, MVector4D, MQuaternion, MMatrix4x4 # noqa
from utils.MLogger import MLogger # noqa

logger = MLogger(__name__)


class ArmPanel(BasePanel):
    
    def __init__(self, frame: wx.Frame, parent: wx.Notebook, tab_idx: int):
        super().__init__(frame, parent, tab_idx)

        # 剛体リスト
        self.avoidance_set_dict = {}
        # 剛体用ダイアログ
        self.avoidance_dialog = AvoidanceDialog(self.frame)

        avoidance_tooltip = "Avoid contact between bone-tracking rigid bodies with the specified name and the wrist/fingertips.\n" \
                            + "Select the bone-tracking rigid bodies you want to avoid from the target model using the select button.\n" \
                            + "\"Head Contact Avoidance\" automatically calculates a spherical rigid body centered on the head."
        alignment_tooltip = "Adjust the wrist position of the target model so that it roughly matches the source model's wrist position."

        # Bulk用接触回避データ
        self.bulk_avoidance_set_dict = {}

        self.description_txt = wx.StaticText(self, wx.ID_ANY, "You can adjust the arms to match the target model.\nYou can execute both \"Contact Avoidance\" and \"Alignment\" together. (Contact Avoidance → Alignment)" + \
                                             "\nArm movement may change from the original motion. Both processes take some time.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.sizer.Add(self.description_txt, 0, wx.ALL, 5)

        self.static_line01 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        self.sizer.Add(self.static_line01, 0, wx.EXPAND | wx.ALL, 5)

        # 剛体接触回避 ----------------
        self.avoidance_title_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 剛体接触回避タイトル
        self.avoidance_title_txt = wx.StaticText(self, wx.ID_ANY, u"Contact Avoidance", wx.DefaultPosition, wx.DefaultSize, 0)
        self.avoidance_title_txt.SetToolTip(avoidance_tooltip)
        self.avoidance_title_txt.Wrap(-1)
        self.avoidance_title_txt.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString))
        self.avoidance_title_txt.Bind(wx.EVT_LEFT_DOWN, self.on_check_arm_process_avoidance)

        self.arm_process_flg_avoidance = wx.CheckBox(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize)
        self.arm_process_flg_avoidance.SetToolTip(avoidance_tooltip)
        self.arm_process_flg_avoidance.Bind(wx.EVT_CHECKBOX, self.set_output_vmd_path)
        self.avoidance_title_sizer.Add(self.arm_process_flg_avoidance, 0, wx.ALL, 5)
        self.avoidance_title_sizer.Add(self.avoidance_title_txt, 0, wx.ALL, 5)
        self.sizer.Add(self.avoidance_title_sizer, 0, wx.ALL, 5)

        # 剛体接触回避説明文
        self.avoidance_description_txt = wx.StaticText(self, wx.ID_ANY, avoidance_tooltip, wx.DefaultPosition, wx.DefaultSize, 0)
        self.sizer.Add(self.avoidance_description_txt, 0, wx.ALL, 5)

        self.avoidance_target_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 剛体名指定
        self.avoidance_target_txt_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", wx.DefaultPosition, (450, 80), wx.HSCROLL | wx.VSCROLL | wx.TE_MULTILINE | wx.TE_READONLY)
        self.avoidance_target_txt_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        self.avoidance_target_txt_ctrl.Bind(wx.EVT_TEXT, self.on_check_arm_process_avoidance)
        self.avoidance_target_sizer.Add(self.avoidance_target_txt_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        self.avoidance_target_btn_ctrl = wx.Button(self, wx.ID_ANY, u"Select Rigid Body", wx.DefaultPosition, wx.DefaultSize, 0)
        self.avoidance_target_btn_ctrl.SetToolTip(u"You can select bone-tracking rigid bodies in the target model")
        self.avoidance_target_btn_ctrl.Bind(wx.EVT_BUTTON, self.on_click_avoidance_target)
        self.avoidance_target_sizer.Add(self.avoidance_target_btn_ctrl, 0, wx.ALIGN_BOTTOM | wx.ALL, 5)

        self.sizer.Add(self.avoidance_target_sizer, 0, wx.ALL, 0)

        self.static_line03 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        self.sizer.Add(self.static_line03, 0, wx.EXPAND | wx.ALL, 5)

        # 手首位置合わせ --------------------
        self.alignment_title_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 手首位置合わせタイトル
        self.alignment_title_txt = wx.StaticText(self, wx.ID_ANY, u"Alignment", wx.DefaultPosition, wx.DefaultSize, 0)
        self.alignment_title_txt.SetToolTip("Adjust motions such as joining hands or touching the floor, to match the wrist position of the target model.\n" + \
                                            "You can adjust the effective range of alignment by adjusting each distance.")
        self.alignment_title_txt.Wrap(-1)
        self.alignment_title_txt.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString))
        self.alignment_title_txt.Bind(wx.EVT_LEFT_DOWN, self.on_check_arm_process_alignment)

        self.arm_process_flg_alignment = wx.CheckBox(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize)
        self.arm_process_flg_alignment.SetToolTip(alignment_tooltip)
        self.arm_process_flg_alignment.Bind(wx.EVT_CHECKBOX, self.set_output_vmd_path)
        self.alignment_title_sizer.Add(self.arm_process_flg_alignment, 0, wx.ALL, 5)
        self.alignment_title_sizer.Add(self.alignment_title_txt, 0, wx.ALL, 5)
        self.sizer.Add(self.alignment_title_sizer, 0, wx.ALL, 5)

        # 手首位置合わせ説明文
        self.alignment_description_txt = wx.StaticText(self, wx.ID_ANY, alignment_tooltip, wx.DefaultPosition, wx.DefaultSize, 0)
        self.sizer.Add(self.alignment_description_txt, 0, wx.ALL, 5)

        # オプションサイザー
        self.alignment_option_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 指位置合わせ
        self.arm_alignment_finger_flg_ctrl = wx.CheckBox(self, wx.ID_ANY, u"Align by finger position", wx.DefaultPosition, wx.DefaultSize, 0)
        self.arm_alignment_finger_flg_ctrl.SetToolTip(u"If checked, you can adjust the wrist position based on the distance between fingers, useful for finger-tutting motions.\nFor multi-person motions, it's better to leave it OFF for cleaner results.")
        self.arm_alignment_finger_flg_ctrl.Bind(wx.EVT_CHECKBOX, self.on_check_arm_process_alignment)
        self.alignment_option_sizer.Add(self.arm_alignment_finger_flg_ctrl, 0, wx.ALL, 5)

        # 床位置合わせ
        self.arm_alignment_floor_flg_ctrl = wx.CheckBox(self, wx.ID_ANY, u"Align with the floor as well", wx.DefaultPosition, wx.DefaultSize, 0)
        self.arm_alignment_floor_flg_ctrl.SetToolTip(u"If checked, you can adjust the wrist position to match the source model when the wrist sinks into or floats above the floor.\nThe center position will also be adjusted together.")
        self.arm_alignment_floor_flg_ctrl.Bind(wx.EVT_CHECKBOX, self.on_check_arm_process_alignment)
        self.alignment_option_sizer.Add(self.arm_alignment_floor_flg_ctrl, 0, wx.ALL, 5)

        self.sizer.Add(self.alignment_option_sizer, 0, wx.ALL, 5)

        # 手首位置スライダー
        self.alignment_distance_wrist_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.alignment_distance_wrist_txt = wx.StaticText(self, wx.ID_ANY, u"Wrist Distance    ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.alignment_distance_wrist_txt.SetToolTip(u"Specify how close the wrists should be to execute wrist alignment.\nSmaller values mean alignment happens only when wrists are close.\nThe unit of distance is the size of the palm of the source model." \
                                                     + "\nDuring sizing, the wrist distance is shown in the message area for reference.\nSetting the slider to maximum always performs wrist alignment. (Useful for two-handed sword, etc.)")
        self.alignment_distance_wrist_txt.Wrap(-1)
        self.alignment_distance_wrist_sizer.Add(self.alignment_distance_wrist_txt, 0, wx.ALL, 5)

        self.alignment_distance_wrist_label = wx.StaticText(self, wx.ID_ANY, u"(1.7)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.alignment_distance_wrist_label.SetToolTip(u"The currently specified wrist distance. If the wrist positions of the source model are within this range, wrist alignment will be performed.")
        self.alignment_distance_wrist_label.Wrap(-1)
        self.alignment_distance_wrist_sizer.Add(self.alignment_distance_wrist_label, 0, wx.ALL, 5)

        self.alignment_distance_wrist_slider = FloatSliderCtrl(self, wx.ID_ANY, 1.7, 0, 10, 0.1, self.alignment_distance_wrist_label, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL)
        self.alignment_distance_wrist_slider.Bind(wx.EVT_SCROLL_CHANGED, self.on_check_arm_process_alignment)
        self.alignment_distance_wrist_sizer.Add(self.alignment_distance_wrist_slider, 1, wx.ALL | wx.EXPAND, 5)

        self.sizer.Add(self.alignment_distance_wrist_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # 指位置スライダー
        self.alignment_distance_finger_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.alignment_distance_finger_txt = wx.StaticText(self, wx.ID_ANY, u"Finger Distance      ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.alignment_distance_finger_txt.SetToolTip(u"Specify how close the fingers should be to execute finger alignment.\nSmaller values mean alignment happens only when fingers are close.\nThe unit of distance is the size of the palm of the source model.\n" \
                                                      + "\nDuring sizing, the finger distance is shown in the message area for reference.\nSetting the slider to maximum always performs finger alignment.")
        self.alignment_distance_finger_txt.Wrap(-1)
        self.alignment_distance_finger_sizer.Add(self.alignment_distance_finger_txt, 0, wx.ALL, 5)

        self.alignment_distance_finger_label = wx.StaticText(self, wx.ID_ANY, u"(1.4)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.alignment_distance_finger_label.SetToolTip(u"The currently specified finger distance. If the finger positions of the source model are within this range, finger alignment will be performed.")
        self.alignment_distance_finger_label.Wrap(-1)
        self.alignment_distance_finger_sizer.Add(self.alignment_distance_finger_label, 0, wx.ALL, 5)

        self.alignment_distance_finger_slider = FloatSliderCtrl(self, wx.ID_ANY, 1.4, 0, 10, 0.1, self.alignment_distance_finger_label, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL)
        self.alignment_distance_finger_slider.Bind(wx.EVT_SCROLL_CHANGED, self.on_check_arm_process_alignment)
        self.alignment_distance_finger_sizer.Add(self.alignment_distance_finger_slider, 1, wx.ALL | wx.EXPAND, 5)

        self.sizer.Add(self.alignment_distance_finger_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # 手首と床との位置スライダー
        self.alignment_distance_floor_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.alignment_distance_floor_txt = wx.StaticText(self, wx.ID_ANY, u"Wrist-Floor Distance", wx.DefaultPosition, wx.DefaultSize, 0)
        self.alignment_distance_floor_txt.SetToolTip(u"Specify how close the wrist and floor should be to execute wrist-floor alignment.\nSmaller values mean alignment is performed only when wrist and floor are close.\nThe unit of distance is the size of the palm of the source model." \
                                                     + "\nDuring sizing, the wrist-floor distance is shown in the message area for reference.\nSetting the slider to maximum always performs wrist-floor alignment.")
        self.alignment_distance_floor_txt.Wrap(-1)
        self.alignment_distance_floor_sizer.Add(self.alignment_distance_floor_txt, 0, wx.ALL, 5)

        self.alignment_distance_floor_label = wx.StaticText(self, wx.ID_ANY, u"(1.2)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.alignment_distance_floor_label.SetToolTip(u"The currently specified wrist-floor distance. If the wrist-floor distance of the source model is within this range, wrist-floor alignment will be performed.")
        self.alignment_distance_floor_label.Wrap(-1)
        self.alignment_distance_floor_sizer.Add(self.alignment_distance_floor_label, 0, wx.ALL, 5)

        self.alignment_distance_floor_slider = FloatSliderCtrl(self, wx.ID_ANY, 1.2, 0, 10, 0.1, self.alignment_distance_floor_label, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL)
        self.alignment_distance_floor_slider.Bind(wx.EVT_SCROLL_CHANGED, self.on_check_arm_process_alignment)
        self.alignment_distance_floor_sizer.Add(self.alignment_distance_floor_slider, 1, wx.ALL | wx.EXPAND, 5)

        self.sizer.Add(self.alignment_distance_floor_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.static_line04 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        self.sizer.Add(self.static_line04, 0, wx.EXPAND | wx.ALL, 5)

        # 腕チェックスキップ --------------------
        self.arm_check_skip_sizer = wx.BoxSizer(wx.VERTICAL)

        self.arm_check_skip_flg_ctrl = wx.CheckBox(self, wx.ID_ANY, u"Skip arm-wrist sizing check", wx.DefaultPosition, wx.DefaultSize, 0)
        self.arm_check_skip_flg_ctrl.SetToolTip(u"Skip the sizing check (not possible if IKArm/腕IK exists) and always perform processing.")
        self.arm_check_skip_sizer.Add(self.arm_check_skip_flg_ctrl, 0, wx.ALL, 5)

        self.arm_check_skip_description = wx.StaticText(self, wx.ID_ANY, u"Skip the arm sizing check (not possible if IKArm/腕IK exists) and always perform arm-related processing.\n" \
                                                        + "* The sizing result may be incorrect, as it is not supported.", \
                                                        wx.DefaultPosition, wx.DefaultSize, 0)
        self.arm_check_skip_description.Wrap(-1)
        self.arm_check_skip_sizer.Add(self.arm_check_skip_description, 0, wx.ALL, 5)
        self.sizer.Add(self.arm_check_skip_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.fit()
        
    def get_avoidance_target(self):
        if len(self.bulk_avoidance_set_dict.keys()) > 0:
            # Bulk用データがある場合、優先返還
            return self.bulk_avoidance_set_dict
        
        target = {}
        if self.arm_process_flg_avoidance.GetValue() == 0:
            return target
        
        # 選択された剛体リストを入力欄に設定(ハッシュが同じ場合のみ)
        if 1 in self.avoidance_set_dict and self.avoidance_set_dict[1].rep_choices:
            if self.avoidance_set_dict[1].equal_hashdigest(self.frame.file_panel_ctrl.file_set):
                target[0] = [self.avoidance_set_dict[1].rep_avoidance_names[n] for n in self.avoidance_set_dict[1].rep_choices.GetSelections()]
            else:
                logger.warning("No.%s: Contact avoidance settings cleared because the file set was changed after setting contact avoidance.", 1, decoration=MLogger.DECORATION_BOX)

        for set_no in list(self.avoidance_set_dict.keys())[1:]:
            if set_no in self.avoidance_set_dict and self.avoidance_set_dict[set_no].rep_choices:
                if len(self.frame.multi_panel_ctrl.file_set_list) >= set_no - 1 and self.avoidance_set_dict[set_no].equal_hashdigest(self.frame.multi_panel_ctrl.file_set_list[set_no - 2]):
                    target[set_no - 1] = [self.avoidance_set_dict[set_no].rep_avoidance_names[n] for n in self.avoidance_set_dict[set_no].rep_choices.GetSelections()]
                else:
                    logger.warning("No.%s: Contact avoidance settings cleared because the file set was changed after setting contact avoidance.", set_no, decoration=MLogger.DECORATION_BOX)

        return target
    
    def on_click_avoidance_target(self, event: wx.Event):
        if self.avoidance_dialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed their mind

        # 一旦クリア
        self.avoidance_target_txt_ctrl.SetValue("")

        # 選択された剛体リストを入力欄に設定
        for set_no, set_data in self.avoidance_set_dict.items():
            # 選択肢ごとの表示文言
            if set_data.rep_choices:
                selections = [set_data.rep_choices.GetString(n) for n in set_data.rep_choices.GetSelections()]
                self.avoidance_target_txt_ctrl.WriteText("No.{0}: {1}\n".format(set_no, ', '.join(selections)))

        self.arm_process_flg_avoidance.SetValue(1)
        self.avoidance_dialog.Hide()

    def initialize(self, event: wx.Event):

        if 1 in self.avoidance_set_dict:
            # ファイルタブ用接触回避のファイルセットがある場合
            if self.frame.file_panel_ctrl.file_set.is_loaded():
                # 既にある場合、ハッシュチェック
                if self.avoidance_set_dict[1].equal_hashdigest(self.frame.file_panel_ctrl.file_set):
                    # 同じである場合、スルー
                    pass
                else:
                    # 違う場合、ファイルセット読み直し
                    self.add_set(1, self.frame.file_panel_ctrl.file_set, replace=True)
            else:
                # ファイルタブが読み込み失敗している場合、読み直し（クリア）
                self.add_set(1, self.frame.file_panel_ctrl.file_set, replace=True)
        else:
            # 空から作る場合、ファイルタブのファイルセット参照
            self.add_set(1, self.frame.file_panel_ctrl.file_set, replace=False)
        
        # multiはあるだけ調べる
        for multi_file_set_idx, multi_file_set in enumerate(self.frame.multi_panel_ctrl.file_set_list):
            set_no = multi_file_set_idx + 2
            if set_no in self.avoidance_set_dict:
                # 複数タブ用接触回避のファイルセットがある場合
                if multi_file_set.is_loaded():
                    # 既にある場合、ハッシュチェック
                    if self.avoidance_set_dict[set_no].equal_hashdigest(multi_file_set):
                        # 同じである場合、スルー
                        pass
                    else:
                        # 違う場合、ファイルセット読み直し
                        self.add_set(set_no, multi_file_set, replace=True)
                    
                        # 複数件ある場合、デフォルト値変更
                        self.set_multi_initialize_value()
                else:
                    # 複数タブが読み込み失敗している場合、読み直し（クリア）
                    self.add_set(set_no, multi_file_set, replace=True)

                    # 複数件ある場合、デフォルト値変更
                    self.set_multi_initialize_value()
            else:
                # 空から作る場合、複数タブのファイルセット参照
                self.add_set(set_no, multi_file_set, replace=False)
            
                # 複数件ある場合、デフォルト値変更
                self.set_multi_initialize_value()

        # 腕系不可モデル名リスト
        disable_arm_model_names = []

        if self.frame.file_panel_ctrl.file_set.is_loaded():
            if not self.frame.file_panel_ctrl.file_set.org_model_file_ctrl.data.can_arm_sizing:
                # 腕不可の場合、リスト追加
                disable_arm_model_names.append("No.1 Source Model: {0}".format(self.frame.file_panel_ctrl.file_set.org_model_file_ctrl.data.name))

            if not self.frame.file_panel_ctrl.file_set.rep_model_file_ctrl.data.can_arm_sizing:
                # 腕不可の場合、リスト追加
                disable_arm_model_names.append("No.1 Target Model: {0}".format(self.frame.file_panel_ctrl.file_set.rep_model_file_ctrl.data.name))

        for multi_file_set_idx, multi_file_set in enumerate(self.frame.multi_panel_ctrl.file_set_list):
            set_no = multi_file_set_idx + 2
            if multi_file_set.is_loaded():
                if not multi_file_set.org_model_file_ctrl.data.can_arm_sizing:
                    # 腕不可の場合、リスト追加
                    disable_arm_model_names.append("No.{0} Source Model: {1}".format(set_no, multi_file_set.org_model_file_ctrl.data.name))

                if not multi_file_set.rep_model_file_ctrl.data.can_arm_sizing:
                    # 腕不可の場合、リスト追加
                    disable_arm_model_names.append("No.{0} Target Model: {1}".format(set_no, multi_file_set.rep_model_file_ctrl.data.name))
            
        if len(disable_arm_model_names) > 0 and not self.arm_check_skip_flg_ctrl.GetValue():
            # 腕不可モデルがいる場合、ダイアログ表示
            with wx.MessageDialog(self, "The following models contain strings related to \"IKArm/腕IK\", so arm-related processing for the corresponding file set\n(Arm Stance Correction, Twist Distribution, Contact Avoidance, Alignment) will be skipped as is.\n" \
                                  + "If you turn ON the arm check skip flag, arm-related processing will be forcibly executed.\n* However, if the result is incorrect, it will not be supported.\n" \
                                  + "Do you want to turn ON the arm check skip flag? \n\n{0}".format('\n'.join(disable_arm_model_names)), style=wx.YES_NO | wx.ICON_WARNING) as dialog:
                if dialog.ShowModal() == wx.ID_NO:
                    # 腕系チェックスキップOFF
                    self.arm_check_skip_flg_ctrl.SetValue(0)
                else:
                    # 腕系チェックスキップON
                    self.arm_check_skip_flg_ctrl.SetValue(1)
                
        event.Skip()
    
    def set_multi_initialize_value(self):
        # 複数件ある場合、手首間の距離デフォルト値変更
        self.alignment_distance_wrist_slider.SetValue(2.5)
        self.alignment_distance_wrist_label.SetLabel("(2.5)")

    def add_set(self, set_idx: int, file_set: SizingFileSet, replace: bool):
        new_avoidance_set = AvoidanceSet(self.frame, self, self.avoidance_dialog.scrolled_window, set_idx, file_set)
        if replace:
            # 置き換え
            self.avoidance_dialog.set_list_sizer.Hide(self.avoidance_set_dict[set_idx].set_sizer, recursive=True)
            self.avoidance_dialog.set_list_sizer.Replace(self.avoidance_set_dict[set_idx].set_sizer, new_avoidance_set.set_sizer, recursive=True)

            # 置き換えの場合、剛体リストクリア
            self.avoidance_target_txt_ctrl.SetValue("")
        else:
            # 新規追加
            self.avoidance_dialog.set_list_sizer.Add(new_avoidance_set.set_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.avoidance_set_dict[set_idx] = new_avoidance_set

        # スクロールバーの表示のためにサイズ調整
        self.avoidance_dialog.set_list_sizer.Layout()
        self.avoidance_dialog.set_list_sizer.FitInside(self.avoidance_dialog.scrolled_window)

    # VMD出力ファイルパス生成
    def set_output_vmd_path(self, event, is_force=False):
        # 念のため出力ファイルパス自動生成（空の場合設定）
        self.frame.file_panel_ctrl.file_set.set_output_vmd_path(event)

        # multiのも出力ファイルパス自動生成（空の場合設定）
        for file_set in self.frame.multi_panel_ctrl.file_set_list:
            file_set.set_output_vmd_path(event)
    
    # 処理対象：接触回避ON
    def on_check_arm_process_avoidance(self, event: wx.Event):
        # テキスト、チェックボックス、実値のいずれかが入った場合、切替
        if isinstance(event.GetEventObject(), wx.StaticText):
            if self.arm_process_flg_avoidance.GetValue() == 0:
                self.arm_process_flg_avoidance.SetValue(1)
            else:
                self.arm_process_flg_avoidance.SetValue(0)

        # パス再生成
        self.set_output_vmd_path(event)
        
        event.Skip()

    # 処理対象：手首位置合わせON
    def on_check_arm_process_alignment(self, event: wx.Event):
        # テキスト、チェックボックス、実値のいずれかが入った場合、切替
        if isinstance(event.GetEventObject(), wx.StaticText):
            if self.arm_process_flg_alignment.GetValue() == 0:
                self.arm_process_flg_alignment.SetValue(1)
            else:
                self.arm_process_flg_alignment.SetValue(0)
        else:
            if self.arm_alignment_finger_flg_ctrl.GetValue() == 1 or self.arm_alignment_floor_flg_ctrl.GetValue() == 1:
                self.arm_process_flg_alignment.SetValue(1)

        if self.arm_alignment_finger_flg_ctrl.GetValue() and len(self.frame.multi_panel_ctrl.file_set_list) > 0:
            self.frame.on_popup_finger_warning(event)

        # パス再生成
        self.set_output_vmd_path(event)

        event.Skip()


class AvoidanceSet():

    def __init__(self, frame: wx.Frame, panel: wx.Panel, window: wx.Window, set_idx: int, file_set: SizingFileSet):
        self.frame = frame
        self.panel = panel
        self.window = window
        self.set_idx = set_idx
        self.file_set = file_set
        self.rep_model_digest = 0 if not file_set.rep_model_file_ctrl.data else file_set.rep_model_file_ctrl.data.digest
        self.rep_avoidances = ["Avoid Head Contact (Head)"]   # 選択肢文言
        self.rep_avoidance_names = ["Avoid Head Contact"]   # 選択肢文言に紐付く剛体名
        self.rep_choices = None

        self.set_sizer = wx.StaticBoxSizer(wx.StaticBox(self.window, wx.ID_ANY, "No.{0}".format(set_idx)), orient=wx.VERTICAL)

        if file_set.is_loaded():
            self.model_name_txt = wx.StaticText(self.window, wx.ID_ANY, file_set.rep_model_file_ctrl.data.name[:15], wx.DefaultPosition, wx.DefaultSize, 0)
            self.model_name_txt.Wrap(-1)
            self.set_sizer.Add(self.model_name_txt, 0, wx.ALL, 5)

            for rigidbody_name, rigidbody in file_set.rep_model_file_ctrl.data.rigidbodies.items():
                # 処理対象剛体：有効なボーン追従剛体
                if rigidbody.isModeStatic() and rigidbody.bone_index in file_set.rep_model_file_ctrl.data.bone_indexes:
                    self.rep_avoidances.append("{0} ({1})".format(rigidbody.name, file_set.rep_model_file_ctrl.data.bone_indexes[rigidbody.bone_index]))
                    self.rep_avoidance_names.append(rigidbody.name)

            # 選択コントロール
            self.rep_choices = wx.ListBox(self.window, id=wx.ID_ANY, choices=self.rep_avoidances, style=wx.LB_MULTIPLE | wx.LB_NEEDED_SB, size=(-1, 220))
            # 頭接触回避はデフォルトで選択
            self.rep_choices.SetSelection(0)
            self.set_sizer.Add(self.rep_choices, 0, wx.ALL, 5)

            # 一括用コピーボタン
            self.copy_btn_ctrl = wx.Button(self.window, wx.ID_ANY, u"Copy for Bulk", wx.DefaultPosition, wx.DefaultSize, 0)
            self.copy_btn_ctrl.SetToolTip(u"Copy contact avoidance data to the clipboard in bulk CSV format")
            self.copy_btn_ctrl.Bind(wx.EVT_BUTTON, self.on_copy)
            self.set_sizer.Add(self.copy_btn_ctrl, 0, wx.ALL, 5)
        else:
            self.no_data_txt = wx.StaticText(self.window, wx.ID_ANY, u"No Data", wx.DefaultPosition, wx.DefaultSize, 0)
            self.no_data_txt.Wrap(-1)
            self.set_sizer.Add(self.no_data_txt, 0, wx.ALL, 5)

    def on_copy(self, event: wx.Event):
        # 一括CSV用モーフテキスト生成
        avoidance_txt_list = []
        for idx in self.rep_choices.GetSelections():
            avoidance_txt_list.append(f"{self.rep_avoidance_names[idx]}")
        # 文末セミコロン
        avoidance_txt_list.append("")

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(";".join(avoidance_txt_list)))
            wx.TheClipboard.Close()

        with wx.TextEntryDialog(self.frame, u"Output contact avoidance data for bulk CSV.\n" \
                                + "When this dialog is displayed, the contact avoidance data below has been copied to the clipboard.\n" \
                                + "If not copied, select the text in the box and paste it into the CSV.", caption=u"Bulk CSV Contact Avoidance Data",
                                value=";".join(avoidance_txt_list), style=wx.TextEntryDialogStyle, pos=wx.DefaultPosition) as dialog:
            dialog.ShowModal()

    # 現在のファイルセットのハッシュと同じであるかチェック
    def equal_hashdigest(self, now_file_set: SizingFileSet):
        return self.rep_model_digest == now_file_set.rep_model_file_ctrl.data.digest


class AvoidanceDialog(wx.Dialog):

    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, title="Select Rigid Body for Avoid Contact", pos=(-1, -1), size=(800, 500), style=wx.DEFAULT_DIALOG_STYLE, name="AvoidanceDialog")

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # 説明文
        self.description_txt = wx.StaticText(self, wx.ID_ANY, u"You can select bone-tracking rigid bodies from the target model to avoid hand contact.\n" \
                                             + u"\"Head Contact Avoidance\" is a rigid body automatically calculated based on head size. If the result is not satisfactory, deselect it.\n" \
                                             + u"There are no restrictions as long as it is a bone-tracking rigid body, but if you select too many, the hand may not be able to avoid anything and unexpected results may occur.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.sizer.Add(self.description_txt, 0, wx.ALL, 5)

        # ボタン
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_btn = wx.Button(self, wx.ID_OK, "OK")
        self.btn_sizer.Add(self.ok_btn, 0, wx.ALL, 5)

        self.calcel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.btn_sizer.Add(self.calcel_btn, 0, wx.ALL, 5)
        self.sizer.Add(self.btn_sizer, 0, wx.ALL, 5)

        self.static_line01 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        self.sizer.Add(self.static_line01, 0, wx.EXPAND | wx.ALL, 5)

        self.scrolled_window = wx.ScrolledWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, \
                                                 wx.FULL_REPAINT_ON_RESIZE | wx.HSCROLL | wx.ALWAYS_SHOW_SB)
        self.scrolled_window.SetScrollRate(5, 5)

        # 接触回避用剛体セット用基本Sizer
        self.set_list_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # スクロールバーの表示のためにサイズ調整
        self.scrolled_window.SetSizer(self.set_list_sizer)
        self.scrolled_window.Layout()
        self.sizer.Add(self.scrolled_window, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        
        # 画面中央に表示
        self.CentreOnScreen()
        
        # 最初は隠しておく
        self.Hide()

