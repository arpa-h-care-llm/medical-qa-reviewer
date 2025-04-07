# This source file is part of the ARPA-H CARE LLM project
#
# SPDX-FileCopyrightText: 2025 Stanford University and the project authors (see AUTHORS.md)
#
# SPDX-License-Identifier: MIT
#
# Author: Vicky Bikia, PhD, Stanford University (bikia@stanford.edu)
#

from abc import ABC, abstractmethod

class ExcelFileColumnInterface(ABC):
    """Abstract interface for Excel file column mappings."""

    @property
    @abstractmethod
    def NOTE_ID(self): pass

    @property
    @abstractmethod
    def QUESTION(self): pass

    @property
    @abstractmethod
    def DISCHARGE_SUMMARY(self): pass

    @property
    @abstractmethod
    def LLM_GENERATED_RESPONSE(self): pass

    @property
    @abstractmethod
    def PROMPT(self): pass

    @property
    @abstractmethod
    def EXPERT_RESPONSE(self): pass


class DischargeSummaryExcelFileColumns(ExcelFileColumnInterface):
    """Default column names for standard medical QA review."""

    @property
    def NOTE_ID(self): return "Note Id"

    @property
    def QUESTION(self): return "Question"

    @property
    def DISCHARGE_SUMMARY(self): return "Discharge Summary"

    @property
    def LLM_GENERATED_RESPONSE(self): return "LLM-generated Response"

    @property
    def PROMPT(self): return "Prompt"

    @property
    def EXPERT_RESPONSE(self): return "Expert's Response"
