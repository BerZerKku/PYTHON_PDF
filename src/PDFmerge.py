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
					pdffile = pdffile[:pos]
					return pdffile.rstrip()

	return name

##
def merge(path, output_filename):
	''' (unicode, str) -> None
		
		Слияние файлов *.pdf.
		В папке \a path ищутся файлы с именем содержащим \a output_filename и
		сливаются в один *.pdf с этим именем.
	'''
	output = PdfFileWriter() 
	output_filename = unicode(output_filename)

	cnt_pdf_file = 0  # счетчик найденных файлов
	for pdffile in glob(u'*.pdf'):
		if pdffile == (output_filename + '.pdf'):
			continue

		if output_filename in pdffile:
			cnt_pdf_file += 1
			document = PdfFileReader(open(pdffile, 'rb'))
			for i in range(document.getNumPages()):
					output.addPage(document.getPage(i))
			print(u"Обработан файл '%s'." % pdffile)

	if cnt_pdf_file == 0:
		print(u"В текущем каталоге небыло найдено подходящих pdf файлов.")
	else:
		output_stream = None
		try:
			print(u"Сохранение в '%s.pdf'." % output_filename)
			output_stream = file(output_filename + '.pdf', "wb")
		except IOError:
			print(u"Ошибка записи!")
			print(u"Попытка сохранения в '%s'." % DEFAULT_NAME)
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
	if not separate:
		merge(args.path, crtOutputName(tmp, FIND))
	else:
		outputname = crtOutputName(tmp, FIND)
		for x in FIND:
			merge(args.path, outputname + " " + x)
	k = raw_input()
