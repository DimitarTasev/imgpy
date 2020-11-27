# Copyright (C) 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

import unittest
from unittest import mock
from unittest.mock import call

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.gui.windows.stack_choice.compare_presenter import StackComparePresenter


class StackChoicePresenterTest(unittest.TestCase):
    def setUp(self):
        self.stack_one = th.generate_images()
        self.stack_two = th.generate_images()
        self.parent = mock.MagicMock()

    @mock.patch("mantidimaging.gui.windows.stack_choice.compare_presenter.StackChoiceView")
    def test_hides_buttons(self, view):
        self.presenter = StackComparePresenter(stack_one=self.stack_one, stack_two=self.stack_two, parent=self.parent)
        view.return_value.originalDataButton.hide.assert_called_once()
        view.return_value.newDataButton.hide.assert_called_once()

    @mock.patch("mantidimaging.gui.windows.stack_choice.compare_presenter.StackChoiceView")
    def test_sets_choice_made(self, view):
        self.presenter = StackComparePresenter(stack_one=self.stack_one, stack_two=self.stack_two, parent=self.parent)
        self.assertIs(view.return_value.choice_made, True)

    @mock.patch("mantidimaging.gui.windows.stack_choice.compare_presenter.StackChoiceView")
    def test_show(self, view):
        self.presenter = StackComparePresenter(stack_one=self.stack_one, stack_two=self.stack_two, parent=self.parent)
        self.presenter.show()

        view.return_value.show.assert_called_once()

    @mock.patch("mantidimaging.gui.windows.stack_choice.compare_presenter.StackChoiceView")
    def test_titles_set(self, view: mock.Mock):
        stack_name = "stack_name"
        custom_parent = mock.MagicMock()
        custom_parent.find_images_stack_title.return_value = stack_name

        self.presenter = StackComparePresenter(stack_one=self.stack_one, stack_two=self.stack_two, parent=custom_parent)

        custom_parent.find_images_stack_title.assert_has_calls([call(self.stack_one), call(self.stack_two)])
        self.assertEqual(2, custom_parent.find_images_stack_title.call_count)
        view.return_value.originalStackLabel.setText.assert_called_once_with(stack_name)
        view.return_value.newStackLabel.setText.assert_called_once_with(stack_name)
