# -*- coding: utf-8 -*-
#
import os
import wx
import wx.lib.newevent

from form.parts.BaseFilePickerCtrl import BaseFilePickerCtrl
from form.parts.HistoryFilePickerCtrl import HistoryFilePickerCtrl
from module.MMath import MRect, MVector3D, MVector4D, MQuaternion, MMatrix4x4  # noqa
from mmd.PmxData import PmxModel
from utils import MServiceUtils, MFileUtils  # noqa
from utils.MLogger import MLogger  # noqa

logger = MLogger(__name__)


class SizingFileSet:
    def __init__(self, frame: wx.Frame, panel: wx.Panel, file_hitories: dict, set_no):
        self.file_hitories = file_hitories
        self.frame = frame
        self.panel = panel
        self.set_no = set_no
        self.STANCE_DETAIL_CHOICES = [
            "センターXZ補正",
            "上半身補正",
            "下半身補正",
            "足ＩＫ補正",
            "つま先補正",
            "つま先ＩＫ補正",
            "肩補正",
            "センターY補正",
        ]
        self.selected_stance_details = [0, 1, 2, 4, 5, 6, 7]

        if self.set_no == 1:
            # ファイルパネルのはそのまま追加
            self.set_sizer = wx.BoxSizer(wx.VERTICAL)
        else:
            self.set_sizer = wx.StaticBoxSizer(
                wx.StaticBox(self.panel, wx.ID_ANY, "【No.{0}】".format(set_no)),
                orient=wx.VERTICAL,
            )

        able_aster_toottip = (
            "You can size multiple data at once by using an asterisk (*) in the file name."
            if self.set_no == 1
            else "Batch specification is not available."
        )
        # VMD/VPDファイルコントロール
        self.motion_vmd_file_ctrl = HistoryFilePickerCtrl(
            frame,
            panel,
            "Target Motion VMD/VPD",
            "Open target motion VMD/VPD file",
            ("vmd", "vpd"),
            wx.FLP_DEFAULT_STYLE,
            "Specify the VMD/VPD path of the motion you want to adjust.\nYou can specify by D&D, open button, or select from history.\n{0}".format(
                able_aster_toottip
            ),
            file_model_spacer=46,
            title_parts_ctrl=None,
            title_parts2_ctrl=None,
            file_histories_key="vmd",
            is_change_output=True,
            is_aster=True,
            is_save=False,
            set_no=set_no,
        )
        self.set_sizer.Add(self.motion_vmd_file_ctrl.sizer, 1, wx.EXPAND, 0)

        # 作成元のスタンス詳細再現FLG
        detail_stance_flg_ctrl = wx.CheckBox(
            panel, wx.ID_ANY, "Add Stance Correction", wx.DefaultPosition, wx.DefaultSize, 0
        )
        detail_stance_flg_ctrl.SetToolTip(
            "If checked, you can add detailed stance corrections.\nFor details, press the '*' button next to it."
        )
        detail_stance_flg_ctrl.Bind(wx.EVT_CHECKBOX, self.set_output_vmd_path)

        # スタンス補正
        detail_btn_ctrl = wx.Button(
            panel, wx.ID_ANY, "*", wx.DefaultPosition, (20, 20), 0
        )
        detail_btn_ctrl.SetToolTip(
            "You can check the breakdown of additional stance corrections and select/deselect them."
        )
        detail_btn_ctrl.Bind(wx.EVT_BUTTON, self.select_detail)

        # 作成元PMXファイルコントロール
        self.org_model_file_ctrl = HistoryFilePickerCtrl(
            frame,
            panel,
            "Source Model PMX",
            "Open source model PMX file",
            ("pmx"),
            wx.FLP_DEFAULT_STYLE,
            "Specify the PMX path of the model used for motion creation.\nAccuracy will decrease, but similar size/bone structure models can be substituted.\nYou can specify by D&D, open button, or select from history.",
            file_model_spacer=1,
            title_parts_ctrl=detail_stance_flg_ctrl,
            title_parts2_ctrl=detail_btn_ctrl,
            file_histories_key="org_pmx",
            is_change_output=False,
            is_aster=False,
            is_save=False,
            set_no=set_no,
        )
        self.set_sizer.Add(self.org_model_file_ctrl.sizer, 1, wx.EXPAND, 0)

        # 捩り分散追加FLG
        twist_flg_ctrl = wx.CheckBox(
            panel, wx.ID_ANY, "With Twist Distribution", wx.DefaultPosition, wx.DefaultSize, 0
        )
        twist_flg_ctrl.SetToolTip(
            "If checked, you can add distribution processing for arm twisting, etc.\nIt takes time."
        )
        twist_flg_ctrl.Bind(wx.EVT_CHECKBOX, self.set_output_vmd_path)

        # 変換先PMXファイルコントロール
        self.rep_model_file_ctrl = HistoryFilePickerCtrl(
            frame,
            panel,
            "Target Model PMX",
            "Open target model PMX file",
            ("pmx"),
            wx.FLP_DEFAULT_STYLE,
            "Specify the PMX path of the model you actually want to load the motion into.\nYou can specify by D&D, open button, or select from history.",
            file_model_spacer=18,
            title_parts_ctrl=twist_flg_ctrl,
            title_parts2_ctrl=None,
            file_histories_key="rep_pmx",
            is_change_output=True,
            is_aster=False,
            is_save=False,
            set_no=set_no,
        )
        self.set_sizer.Add(self.rep_model_file_ctrl.sizer, 1, wx.EXPAND, 0)

        # 出力先VMDファイルコントロール
        self.output_vmd_file_ctrl = BaseFilePickerCtrl(
            frame,
            panel,
            "Output VMD",
            "Open output VMD file",
            ("vmd"),
            wx.FLP_OVERWRITE_PROMPT | wx.FLP_SAVE | wx.FLP_USE_TEXTCTRL,
            "Specify the output path for the adjusted VMD.\nFile path is automatically generated based on the VMD file and target PMX file names, but you can also change it to any path.",
            is_aster=False,
            is_save=True,
            set_no=set_no,
        )
        self.set_sizer.Add(self.output_vmd_file_ctrl.sizer, 1, wx.EXPAND, 0)

    def get_selected_stance_details(self):
        # 選択されたINDEXの名称を返す
        return [self.STANCE_DETAIL_CHOICES[n] for n in self.selected_stance_details]

    def select_detail(self, event: wx.Event):
        with wx.MultiChoiceDialog(
            self.panel,
            "Only the corrections that are checked will be applied among the additional stance corrections.",
            caption="Select Additional Stance Corrections",
            choices=self.STANCE_DETAIL_CHOICES,
            style=wx.CHOICEDLG_STYLE,
        ) as choiceDialog:
            choiceDialog.SetSelections(self.selected_stance_details)

            if choiceDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            self.selected_stance_details = choiceDialog.GetSelections()

            if len(self.selected_stance_details) == 0:
                self.org_model_file_ctrl.title_parts_ctrl.SetValue(0)
            else:
                self.org_model_file_ctrl.title_parts_ctrl.SetValue(1)

    def save(self):
        self.motion_vmd_file_ctrl.save()
        self.org_model_file_ctrl.save()
        self.rep_model_file_ctrl.save()

    # フォーム無効化
    def disable(self):
        self.motion_vmd_file_ctrl.disable()
        self.org_model_file_ctrl.disable()
        self.rep_model_file_ctrl.disable()
        self.output_vmd_file_ctrl.disable()

    # フォーム無効化
    def enable(self):
        self.motion_vmd_file_ctrl.enable()
        self.org_model_file_ctrl.enable()
        self.rep_model_file_ctrl.enable()
        self.output_vmd_file_ctrl.enable()

    # ファイル読み込み前のチェック
    def is_valid(self):
        result = True
        if self.set_no == 1:
            # 1番目は必ず調べる
            result = self.motion_vmd_file_ctrl.is_valid() and result
            result = self.org_model_file_ctrl.is_valid() and result
            result = self.rep_model_file_ctrl.is_valid() and result
            result = self.output_vmd_file_ctrl.is_valid() and result
        else:
            # 2番目以降は、ファイルが揃ってたら調べる
            if (
                self.motion_vmd_file_ctrl.is_set_path()
                or self.org_model_file_ctrl.is_set_path()
                or self.rep_model_file_ctrl.is_set_path()
                or self.output_vmd_file_ctrl.is_set_path()
            ):
                result = self.motion_vmd_file_ctrl.is_valid() and result
                result = self.org_model_file_ctrl.is_valid() and result
                result = self.rep_model_file_ctrl.is_valid() and result
                result = self.output_vmd_file_ctrl.is_valid() and result

        return result

    # 入力後の入力可否チェック
    def is_loaded_valid(self):
        if self.set_no == 0:
            # CSVとかのファイルは番号出力なし
            display_set_no = ""
        else:
            display_set_no = "{0}番目の".format(self.set_no)

        # 両方のPMXが読めて、モーションも読み込めた場合、キーチェック
        not_org_standard_bones = []
        not_org_other_bones = []
        not_org_morphs = []
        not_rep_standard_bones = []
        not_rep_other_bones = []
        not_rep_morphs = []
        mismatch_bones = []

        motion = self.motion_vmd_file_ctrl.data
        org_pmx = self.org_model_file_ctrl.data
        rep_pmx = self.rep_model_file_ctrl.data

        if not motion or not org_pmx or not rep_pmx:
            # どれか読めてなければそのまま終了
            return True

        if motion.motion_cnt == 0:
            logger.warning(
                "%sNo keyframes are registered in the bone motion data.",
                display_set_no,
                decoration=MLogger.DECORATION_BOX,
            )
            return True

        result = True
        is_warning = False

        # ボーン
        for k in motion.bones.keys():
            bone_fnos = motion.get_bone_fnos(k)
            for fno in bone_fnos:
                if (
                    motion.bones[k][fno].position != MVector3D()
                    or motion.bones[k][fno].rotation != MQuaternion()
                ):
                    # キーが存在しており、かつ初期値ではない値が入っている場合、警告対象

                    if isinstance(org_pmx, Exception):
                        raise org_pmx

                    if k not in org_pmx.bones:
                        if k in PmxModel.PARENT_BORN_PAIR:
                            not_org_standard_bones.append(k)
                        else:
                            not_org_other_bones.append(k)

                    if isinstance(rep_pmx, Exception):
                        raise rep_pmx

                    if k not in rep_pmx.bones:
                        if k in PmxModel.PARENT_BORN_PAIR:
                            not_rep_standard_bones.append(k)
                        else:
                            not_rep_other_bones.append(k)

                    if k in org_pmx.bones and k in rep_pmx.bones:
                        mismatch_types = []
                        # 両方にボーンがある場合、フラグが同じであるかチェック
                        if (
                            org_pmx.bones[k].getRotatable()
                            != rep_pmx.bones[k].getRotatable()
                        ):
                            mismatch_types.append("Capability: Rotation")
                        if (
                            org_pmx.bones[k].getTranslatable()
                            != rep_pmx.bones[k].getTranslatable()
                        ):
                            mismatch_types.append("Capability: Movement")
                        if org_pmx.bones[k].getIkFlag() != rep_pmx.bones[k].getIkFlag():
                            mismatch_types.append("Capability: IK")
                        if (
                            org_pmx.bones[k].getVisibleFlag()
                            != rep_pmx.bones[k].getVisibleFlag()
                        ):
                            mismatch_types.append("Capability: Visible")
                        if (
                            org_pmx.bones[k].getManipulatable()
                            != rep_pmx.bones[k].getManipulatable()
                        ):
                            mismatch_types.append("Capability: Enabled")
                        if org_pmx.bones[k].display != rep_pmx.bones[k].display:
                            mismatch_types.append("Display Frame")

                        if len(mismatch_types) > 0:
                            mismatch_bones.append(
                                f"{k}   [Difference] {', '.join(mismatch_types)})"
                            )

                    # 1件あればOK
                    break

        for k in motion.morphs.keys():
            morph_fnos = motion.get_morph_fnos(k)
            for fno in morph_fnos:
                if motion.morphs[k][fno].ratio != 0:
                    # キーが存在しており、かつ初期値ではない値が入っている場合、警告対象

                    if k not in org_pmx.morphs:
                        not_org_morphs.append(k)

                    if k not in rep_pmx.morphs:
                        not_rep_morphs.append(k)

                    # 1件あればOK
                    break

        if (
            len(not_org_standard_bones) > 0
            or len(not_org_other_bones) > 0
            or len(not_org_morphs) > 0
        ):
            logger.warning(
                "%s%s is missing bones/morphs used in the motion.\nModel: %s\nMissing bones (up to semi-standard): %s\nMissing bones (others): %s\nMissing morphs: %s",
                display_set_no,
                self.org_model_file_ctrl.title,
                org_pmx.name,
                ",".join(not_org_standard_bones),
                ",".join(not_org_other_bones),
                ",".join(not_org_morphs),
                decoration=MLogger.DECORATION_BOX,
            )
            is_warning = True

        if (
            len(not_rep_standard_bones) > 0
            or len(not_rep_other_bones) > 0
            or len(not_rep_morphs) > 0
        ):
            logger.warning(
                "%s%s is missing bones/morphs used in the motion.\nModel: %s\nMissing bones (up to semi-standard): %s\nMissing bones (others): %s\nMissing morphs: %s",
                display_set_no,
                self.rep_model_file_ctrl.title,
                rep_pmx.name,
                ",".join(not_rep_standard_bones),
                ",".join(not_rep_other_bones),
                ",".join(not_rep_morphs),
                decoration=MLogger.DECORATION_BOX,
            )
            is_warning = True

        if len(mismatch_bones) > 0:
            logger.warning(
                "%s%s has differences in the capabilities etc. of bones used in the motion.\nModel: %s\nDifferent bones:\n　%s",
                display_set_no,
                self.rep_model_file_ctrl.title,
                rep_pmx.name,
                "\n　".join(mismatch_bones),
                decoration=MLogger.DECORATION_BOX,
            )
            is_warning = True

        if not is_warning:
            logger.info(
                "All bones/morphs used in the motion are present.",
                decoration=MLogger.DECORATION_BOX,
                title="OK",
            )

        return result

    def is_loaded(self):
        result = True
        if self.is_valid():
            result = self.motion_vmd_file_ctrl.data and result
            result = self.org_model_file_ctrl.data and result
            result = self.rep_model_file_ctrl.data and result
        else:
            result = False

        return result

    def load(self):
        result = True
        try:
            is_check = not self.frame.arm_panel_ctrl.arm_check_skip_flg_ctrl.GetValue()
            result = self.motion_vmd_file_ctrl.load(is_check=is_check) and result
            result = self.org_model_file_ctrl.load(is_check=is_check) and result
            result = self.rep_model_file_ctrl.load(is_check=is_check) and result
        except Exception:
            result = False

        return result

    # VMD出力ファイルパス生成
    def set_output_vmd_path(self, event, is_force=False):
        output_vmd_path = MFileUtils.get_output_vmd_path(
            self.motion_vmd_file_ctrl.file_ctrl.GetPath(),
            self.rep_model_file_ctrl.file_ctrl.GetPath(),
            self.org_model_file_ctrl.title_parts_ctrl.GetValue(),
            self.rep_model_file_ctrl.title_parts_ctrl.GetValue(),
            self.frame.arm_panel_ctrl.arm_process_flg_avoidance.GetValue(),
            self.frame.arm_panel_ctrl.arm_process_flg_alignment.GetValue(),
            (
                self.set_no in self.frame.morph_panel_ctrl.morph_set_dict
                and self.frame.morph_panel_ctrl.morph_set_dict[
                    self.set_no
                ].is_set_morph()
            )
            or (
                self.set_no in self.frame.morph_panel_ctrl.bulk_morph_set_dict
                and len(self.frame.morph_panel_ctrl.bulk_morph_set_dict[self.set_no])
                > 0
            ),
            self.output_vmd_file_ctrl.file_ctrl.GetPath(),
            is_force,
        )

        self.output_vmd_file_ctrl.file_ctrl.SetPath(output_vmd_path)

        if len(output_vmd_path) >= 255 and os.name == "nt":
            logger.error(
                "File path exceeds Windows limit.\nFile path: {0}".format(
                    output_vmd_path
                ),
                decoration=MLogger.DECORATION_BOX,
            )

    def calc_leg_ik_ratio(self):
        target_bones = ["左足", "左ひざ", "左足首", "センター"]

        if (
            self.is_loaded()
            and set(target_bones).issubset(self.org_model_file_ctrl.data.bones)
            and set(target_bones).issubset(self.rep_model_file_ctrl.data.bones)
        ):
            # 頭身
            _, _, org_heads_tall = MServiceUtils.calc_heads_tall(
                self.org_model_file_ctrl.data
            )
            _, _, rep_heads_tall = MServiceUtils.calc_heads_tall(
                self.rep_model_file_ctrl.data
            )

            # 頭身比率
            heads_tall_ratio = org_heads_tall / rep_heads_tall

            # XZ比率(足の長さ)
            org_leg_length = (
                (
                    self.org_model_file_ctrl.data.bones["左足首"].position
                    - self.org_model_file_ctrl.data.bones["左ひざ"].position
                )
                + (
                    self.org_model_file_ctrl.data.bones["左ひざ"].position
                    - self.org_model_file_ctrl.data.bones["左足"].position
                )
            ).length()
            rep_leg_length = (
                (
                    self.rep_model_file_ctrl.data.bones["左足首"].position
                    - self.rep_model_file_ctrl.data.bones["左ひざ"].position
                )
                + (
                    self.rep_model_file_ctrl.data.bones["左ひざ"].position
                    - self.rep_model_file_ctrl.data.bones["左足"].position
                )
            ).length()
            logger.test(
                "xz_ratio rep_leg_length: %s, org_leg_length: %s",
                rep_leg_length,
                org_leg_length,
            )
            xz_ratio = 1 if org_leg_length == 0 else (rep_leg_length / org_leg_length)

            # Y比率(股下のY差)
            rep_leg_length = (
                self.rep_model_file_ctrl.data.bones["左足首"].position
                - self.rep_model_file_ctrl.data.bones["左足"].position
            ).y()
            org_leg_length = (
                self.org_model_file_ctrl.data.bones["左足首"].position
                - self.org_model_file_ctrl.data.bones["左足"].position
            ).y()
            logger.test(
                "y_ratio rep_leg_length: %s, org_leg_length: %s",
                rep_leg_length,
                org_leg_length,
            )
            y_ratio = 1 if org_leg_length == 0 else (rep_leg_length / org_leg_length)

            return xz_ratio, y_ratio, heads_tall_ratio

        return 1, 1, 1
