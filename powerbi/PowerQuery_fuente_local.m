// Crear parámetro RutaJSON con la ruta completa al JSON; cambiar Section para cada tabla.
let
    Source = Json.Document(File.Contents(RutaJSON)),
    Section = Source[cube],
    Rows = Table.FromRecords(Section),
    Numeric = Table.TransformColumnTypes(Rows, {{"Year",Int64.Type},{"Month",Int64.Type},{"ops",Int64.Type},{"ontime",Int64.Type},{"delayed15",Int64.Type},{"delayed60",Int64.Type},{"cancel",Int64.Type},{"divert",Int64.Type},{"sumDelayMin",type number},{"carrierDelay",type number},{"weatherDelay",type number},{"nasDelay",type number},{"secDelay",type number},{"lateAirDelay",type number}}),
    Gap = Table.AddColumn(Numeric,"CauseGap", each [carrierDelay]+[weatherDelay]+[nasDelay]+[secDelay]+[lateAirDelay]-[sumDelayMin],type number),
    Valid = Table.AddColumn(Gap,"CauseValid",each Number.Abs([CauseGap])<=1,type logical),
    Residual = Table.AddColumn(Valid,"Unclassified",each [ops]-[ontime]-[delayed15]-[cancel]-[divert],Int64.Type),
    Period = Table.AddColumn(Residual,"Period",each Text.From([Year])&"-"&Text.PadStart(Text.From([Month]),2,"0"),type text),
    Index = Table.AddIndexColumn(Period,"RowId",1,1,Int64.Type)
in Index
