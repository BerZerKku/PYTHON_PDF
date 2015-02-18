# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from glob import glob
from pyPdf import PdfFileReader, PdfFileWriter
import sys, os, locale

FIND = [u"(СБ)", u"(СП)", u"(Э3)"]  # признак поиска
DEFAULT_NAME = "merged"  # название файла по умолчанию

##
def crtOutputName(name, find):
	''' (unicode, list of unicode) -> (unicode)
		
		Возвращает имя файла.
		Если в \a name передается название по умолчанию, в текущем каталоге
		будет осуществлен поиск по признаку \a find. Имя будет сформированно
		из первого найденного файла, удовлетворяющего строке поиска. Иначе
		будет возвращено имя указанное в \a name.
		
	'''
	if name == DEFAULT_NAME:
		for pdffile in glob(u'*.pdf'):
			for f in find:
				# поиск среди pdf, файлов с именем содержащим хотя бы одну
				# строку из find
				pos = pdffile.find(f)
				if pos >= 0:
					# если файл был найден, оставим в нем только то
					# что находится до содержимого поиска
					# так же убираются лишние пробелы в конце
					name = pdffile[:pos]
	else:
		pos = name.find(".pdf")
		if pos >= 0:
			name = name[:pos]
	
	return name.rstrip()

##
def crtFullDocument(path, output_filename, find):
	''' (unicode, unicode, list of unicode) -> None
	
		Сборка всех файлов документации в один файл.
	'''
	output_filename = unicode(output_filename)
	input_files = []
	files = glob(u'*.pdf')
	# создается список возможных файлов и они затем ищутся в текущем каталоге
	for f in [u"%s %s.pdf" % (output_filename, x) for x in find]:
		if f in files:
			input_files.append(f)
		
	merge(path, u"%s.pdf" % (output_filename), input_files)
	

##
def crtSeparateDocuments(path, output_filename, find):
	''' (unicode, unicode, list of unicode) -> None
	
		Сборка раздельных файлов документации.
	'''
	output_filename = unicode(output_filename)
	files = glob(u'*.pdf')
	# создается маска для поиска файлов одинаковой документации и затем
	# по этой маске выбираются файлы из текущего каталога
	for doc in find:
		input_files = []
		input_mask = u"%s %s " % (output_filename, doc)
		output_filename = u"%s %s.pdf" % (output_filename, doc)
		for f in files:
			if input_mask in f:
				input_files.append(f)
		
		merge(path, output_filename, input_files)
	# pass
	
##
def merge(path, output_filename, input_files):
	''' (unicode, unicode, list of unicode) -> None
		
		Слияние файлов *.pdf.
		Копирование всех страниц из файлов списка \a input_files (c учетом
		расширения) в один выходной файл с именем \a output_filename.
	'''
	output = PdfFileWriter() 
	output_filename = unicode(output_filename)
	
	cnt_pdf_file = 0  # счетчик найденных файлов
	for f in input_files:
		cnt_pdf_file += 1
		document = PdfFileReader(open(f, 'rb'))
		for i in range(document.getNumPages()):
			output.addPage(document.getPage(i))
		print(u"Обработан файл '%s'." % f)

	if cnt_pdf_file == 0:
		print(u"В текущем каталоге небыло найдено подходящих pdf файлов.")
	else:
		output_stream = None
		try:
			print(u"Сохранение в '%s'." % output_filename)
			output_stream = file(output_filename, "wb")
		except IOError:
			print(u"Ошибка записи!")
			print(u"Попытка сохранения в %s.pdf" % DEFAULT_NAME)
			try:
				output_stream = file(DEFAULT_NAME + '.pdf', "wb")
			except:
				print(u"Ошибка записи!")

		if output_stream is not None:
			output.write(output_stream)
			output_stream.close()

##
if __name__ == "__main__":
	parser = ArgumentParser()

	# Add more options if you like
	parser.add_argument("-o", "--output", dest="output_filename",
						default=DEFAULT_NAME,
						help=u"write merged PDF to FILE", metavar="FILE")
	parser.add_argument("-p", "--path", dest="path", default=".",
						help=u"path of source PDF files")
	parser.add_argument("-s", "--separate", help="create separate documents",
                    action="store_true")

	args = parser.parse_args()
	separate = args.separate
	tmp = unicode(args.output_filename, locale.getpreferredencoding())
	
	outputname = crtOutputName(tmp, FIND)
	crtSeparateDocuments(args.path, outputname, FIND)
	crtFullDocument(args.path, outputname, FIND)
		
	k = raw_input()
