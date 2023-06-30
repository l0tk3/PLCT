mdfile=open("./table.md","r+")
csvfile=open("./res.csv","w+")
md=mdfile.read()
mdfile.close()
md=md.split("\n")
del(md[1])
for i in md:
    i=i[1:-1]
    i=i.replace('|',',')
    csvfile.write(i+"\n")
csvfile.close()